"""Unit tests for DeleteAccountUseCase."""

import uuid
import pytest

from src.features.users.application.delete_account_use_case import DeleteAccountUseCase
from src.features.users.application.exceptions import InvalidCredentialsException
from src.features.users.application.ports import IUnitOfWork
from src.features.users.data.auth.bcrypt_hasher import BcryptPasswordHasher
from src.features.users.domain.models import Device, Persona, User
from src.features.users.domain.ports import (
    IDeviceRepository,
    IPasswordHasher,
    IPersonaRepository,
    IUserRepository,
)


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


class InMemoryDeviceRepository(IDeviceRepository):
    def __init__(self):
        self.devices = {}

    def save(self, device: Device) -> None:
        self.devices[device.id] = device

    def find_by_android_id(self, android_id: str):
        for d in self.devices.values():
            if d.android_id == android_id:
                return d
        return None

    def delete_by_user_id(self, user_id: uuid.UUID) -> None:
        to_delete = [d.id for d in self.devices.values() if d.user_id == user_id]
        for d_id in to_delete:
            del self.devices[d_id]


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
def setup_account():
    hasher = BcryptPasswordHasher()
    hashed = hasher.hash("CorrectPassword123")

    uow = FakeUnitOfWork()
    user_repo = InMemoryUserRepository()
    persona_repo = InMemoryPersonaRepository()
    device_repo = InMemoryDeviceRepository()

    persona = Persona(
        id=uuid.uuid4(),
        first_name="Maria",
        last_name="Lopez",
        identity_card="8765432",
        phone="71234567",
    )
    persona_repo.save(persona)

    user = User(
        id=uuid.uuid4(),
        persona_id=persona.id,
        email="maria.lopez@example.com",
        password_hash=hashed,
        role="patient",
    )
    user_repo.save(user)

    device = Device(
        id=uuid.uuid4(),
        user_id=user.id,
        android_id="device-maria-001",
    )
    device_repo.save(device)

    use_case = DeleteAccountUseCase(
        uow=uow,
        user_repo=user_repo,
        persona_repo=persona_repo,
        device_repo=device_repo,
        password_hasher=hasher,
    )

    return {
        "uow": uow,
        "user_repo": user_repo,
        "persona_repo": persona_repo,
        "device_repo": device_repo,
        "user": user,
        "persona": persona,
        "device": device,
        "use_case": use_case,
    }


def test_delete_account_success(setup_account):
    """Account deletion with correct password succeeds and releases all entities."""
    use_case = setup_account["use_case"]
    user = setup_account["user"]
    persona = setup_account["persona"]
    device = setup_account["device"]

    result = use_case.execute(user_id=user.id, password="CorrectPassword123")

    assert "message" in result
    assert "Cuenta eliminada exitosamente" in result["message"]
    assert setup_account["uow"].committed is True

    # Verify User, Persona, and Device are deleted
    assert setup_account["user_repo"].find_by_id(user.id) is None
    assert setup_account["persona_repo"].find_by_id(persona.id) is None
    assert setup_account["persona_repo"].find_by_identity_card(persona.identity_card) is None
    assert setup_account["device_repo"].find_by_android_id(device.android_id) is None


def test_delete_account_incorrect_password(setup_account):
    """Account deletion fails with incorrect password and keeps all entities."""
    use_case = setup_account["use_case"]
    user = setup_account["user"]
    persona = setup_account["persona"]
    device = setup_account["device"]

    with pytest.raises(InvalidCredentialsException):
        use_case.execute(user_id=user.id, password="WrongPassword999")

    # Verify no records were deleted
    assert setup_account["user_repo"].find_by_id(user.id) is not None
    assert setup_account["persona_repo"].find_by_id(persona.id) is not None
    assert setup_account["device_repo"].find_by_android_id(device.android_id) is not None


def test_delete_account_user_not_found(setup_account):
    """Account deletion with non-existent user ID raises InvalidCredentialsException."""
    use_case = setup_account["use_case"]

    with pytest.raises(InvalidCredentialsException):
        use_case.execute(user_id=uuid.uuid4(), password="CorrectPassword123")

