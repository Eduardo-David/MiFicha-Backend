"""Unit tests for UpdateProfileUseCase."""

import uuid
from datetime import datetime, timedelta, timezone
import pytest

from src.features.users.application.exceptions import (
    EntityAlreadyExistsException,
    InvalidCredentialsException,
)
from src.features.users.application.ports import IUnitOfWork
from src.features.users.application.update_profile_use_case import UpdateProfileUseCase
from src.features.users.domain.exceptions import RestriccionTiempoException, ValidationError
from src.features.users.domain.models import Persona, User
from src.features.users.domain.ports import IPersonaRepository, IUserRepository


class InMemoryUserRepository(IUserRepository):
    def __init__(self):
        self.users = {}

    def save(self, user: User) -> None:
        self.users[user.id] = user

    def find_by_id(self, user_id: uuid.UUID):
        return self.users.get(user_id)

    def find_by_email(self, email: str):
        for u in self.users.values():
            if u.email == email:
                return u
        return None

    def delete(self, user_id: uuid.UUID) -> None:
        if user_id in self.users:
            del self.users[user_id]


class InMemoryPersonaRepository(IPersonaRepository):
    def __init__(self):
        self.personas = {}

    def save(self, persona: Persona) -> None:
        self.personas[persona.id] = persona

    def find_by_id(self, persona_id: uuid.UUID):
        return self.personas.get(persona_id)

    def find_by_identity_card(self, identity_card: str):
        for p in self.personas.values():
            if p.identity_card == identity_card:
                return p
        return None

    def delete(self, persona_id: uuid.UUID) -> None:
        if persona_id in self.personas:
            del self.personas[persona_id]


class FakeUnitOfWork(IUnitOfWork):
    def __init__(self):
        self.committed = False
        self.rolled_back = False

    def __enter__(self) -> IUnitOfWork:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self.rollback()

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


@pytest.fixture
def repos():
    uow = FakeUnitOfWork()
    user_repo = InMemoryUserRepository()
    persona_repo = InMemoryPersonaRepository()

    persona_id = uuid.uuid4()
    persona = Persona(
        id=persona_id,
        first_name="Juan",
        last_name="Perez",
        identity_card="1234567",
        phone="71234567",
    )
    persona_repo.save(persona)

    user_id = uuid.uuid4()
    # 25 hours ago, so cooldown is expired
    past_time = datetime.now(timezone.utc) - timedelta(hours=25)
    user = User(
        id=user_id,
        persona_id=persona_id,
        email="juan.perez@example.com",
        password_hash="hashed_pw",
        role="patient",
        last_profile_update=past_time,
    )
    user_repo.save(user)

    use_case = UpdateProfileUseCase(
        uow=uow,
        user_repo=user_repo,
        persona_repo=persona_repo,
    )

    return {
        "uow": uow,
        "user_repo": user_repo,
        "persona_repo": persona_repo,
        "user": user,
        "persona": persona,
        "use_case": use_case,
    }


def test_update_profile_success(repos):
    """Profile update succeeds when cooldown period has elapsed."""
    use_case = repos["use_case"]
    user = repos["user"]

    result = use_case.execute(
        user_id=user.id,
        new_email="juan.nuevo@example.com",
        new_phone="79876543",
    )

    assert result["email"] == "juan.nuevo@example.com"
    assert result["phone"] == "79876543"
    assert repos["uow"].committed is True

    # Check persistence
    updated_user = repos["user_repo"].find_by_id(user.id)
    assert updated_user.email == "juan.nuevo@example.com"

    updated_persona = repos["persona_repo"].find_by_id(user.persona_id)
    assert updated_persona.phone == "79876543"


def test_update_profile_cooldown_rejection(repos):
    """Profile update fails if less than 24 hours have passed since last update."""
    use_case = repos["use_case"]
    user = repos["user"]

    # Set last_profile_update to 2 hours ago
    user.last_profile_update = datetime.now(timezone.utc) - timedelta(hours=2)

    with pytest.raises(RestriccionTiempoException) as exc_info:
        use_case.execute(
            user_id=user.id,
            new_email="juan.too.soon@example.com",
        )

    assert "Profile modification is locked" in str(exc_info.value)
    assert exc_info.value.time_remaining.total_seconds() > 0


def test_update_profile_duplicate_email(repos):
    """Profile update fails if new email is already registered by another user."""
    use_case = repos["use_case"]
    user = repos["user"]
    user_repo = repos["user_repo"]

    # Register another user
    other_user = User(
        id=uuid.uuid4(),
        persona_id=uuid.uuid4(),
        email="other@example.com",
        password_hash="other_pw",
        role="patient",
    )
    user_repo.save(other_user)

    with pytest.raises(EntityAlreadyExistsException) as exc_info:
        use_case.execute(
            user_id=user.id,
            new_email="other@example.com",
        )

    assert exc_info.value.field == "email"


def test_update_profile_same_email_allowed(repos):
    """User can submit their current email without triggering uniqueness error."""
    use_case = repos["use_case"]
    user = repos["user"]

    result = use_case.execute(
        user_id=user.id,
        new_email="juan.perez@example.com",
        new_phone="68765432",
    )

    assert result["email"] == "juan.perez@example.com"
    assert result["phone"] == "68765432"


def test_update_profile_invalid_phone(repos):
    """Invalid Bolivian phone number format raises ValidationError."""
    use_case = repos["use_case"]
    user = repos["user"]

    with pytest.raises(ValidationError) as exc_info:
        use_case.execute(
            user_id=user.id,
            new_phone="12345",  # Invalid prefix and length
        )

    assert exc_info.value.field == "phone"


def test_update_profile_invalid_email(repos):
    """Invalid email format raises ValidationError."""
    use_case = repos["use_case"]
    user = repos["user"]

    with pytest.raises(ValidationError) as exc_info:
        use_case.execute(
            user_id=user.id,
            new_email="not-an-email",
        )

    assert exc_info.value.field == "email"


def test_update_profile_user_not_found(repos):
    """Non-existent user raises InvalidCredentialsException."""
    use_case = repos["use_case"]

    with pytest.raises(InvalidCredentialsException):
        use_case.execute(
            user_id=uuid.uuid4(),
            new_email="nonexistent@example.com",
        )

