"""Integration tests for user profile update endpoint (PUT /api/v1/usuarios/perfil)."""

import uuid
from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.features.users.application.ports import IUnitOfWork
from src.features.users.domain.models import Persona, User
from src.features.users.domain.ports import IPersonaRepository, IUserRepository
from src.features.users.data.auth.jwt_service import PyJWTTokenService
from src.features.users.presentation.routes import (
    get_persona_repository,
    get_unit_of_work,
    get_user_repository,
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
def test_setup():
    uow = FakeUnitOfWork()
    user_repo = InMemoryUserRepository()
    persona_repo = InMemoryPersonaRepository()

    persona_id = uuid.uuid4()
    persona = Persona(
        id=persona_id,
        first_name="Carlos",
        last_name="Arce",
        identity_card="1122334-5B",
        phone="71234567",
    )
    persona_repo.save(persona)

    user_id = uuid.uuid4()
    # 25 hours ago so 24h cooldown has expired
    past_time = datetime.now(timezone.utc) - timedelta(hours=25)
    user = User(
        id=user_id,
        persona_id=persona_id,
        email="carlos.arce@example.com",
        password_hash="some_hash",
        role="patient",
        last_profile_update=past_time,
    )
    user_repo.save(user)

    # Issue JWT token
    token_service = PyJWTTokenService()
    token = token_service.create_access_token({"sub": str(user_id)})

    app.dependency_overrides[get_user_repository] = lambda: user_repo
    app.dependency_overrides[get_persona_repository] = lambda: persona_repo
    app.dependency_overrides[get_unit_of_work] = lambda: uow

    with TestClient(app) as test_client:
        yield {
            "client": test_client,
            "token": token,
            "user": user,
            "persona": persona,
            "user_repo": user_repo,
            "persona_repo": persona_repo,
        }

    app.dependency_overrides.clear()


def test_update_profile_success(test_setup):
    """PUT /api/v1/usuarios/perfil updates email and phone successfully."""
    client = test_setup["client"]
    token = test_setup["token"]
    user_repo = test_setup["user_repo"]
    user = test_setup["user"]

    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "email": "carlos.nuevo@example.com",
        "phone": "79876543",
    }

    response = client.put("/api/v1/usuarios/perfil", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Perfil actualizado exitosamente"
    assert data["email"] == "carlos.nuevo@example.com"
    assert data["phone"] == "79876543"

    # Confirm persistence
    persisted = user_repo.find_by_id(user.id)
    assert persisted.email == "carlos.nuevo@example.com"


def test_update_profile_only_email(test_setup):
    """Updating only email keeps existing phone number."""
    client = test_setup["client"]
    token = test_setup["token"]
    persona = test_setup["persona"]

    headers = {"Authorization": f"Bearer {token}"}
    payload = {"email": "carlos.solo.email@example.com"}

    response = client.put("/api/v1/usuarios/perfil", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "carlos.solo.email@example.com"
    assert data["phone"] == persona.phone


def test_update_profile_only_phone(test_setup):
    """Updating only phone keeps existing email address."""
    client = test_setup["client"]
    token = test_setup["token"]
    user = test_setup["user"]

    headers = {"Authorization": f"Bearer {token}"}
    payload = {"phone": "68765432"}

    response = client.put("/api/v1/usuarios/perfil", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user.email
    assert data["phone"] == "68765432"


def test_update_profile_conflict_duplicate_email(test_setup):
    """Updating to an email already in use returns 409 Conflict."""
    client = test_setup["client"]
    token = test_setup["token"]
    user_repo = test_setup["user_repo"]

    # Register conflicting user
    conflict_user = User(
        id=uuid.uuid4(),
        persona_id=uuid.uuid4(),
        email="conflict@example.com",
        password_hash="hash",
        role="patient",
    )
    user_repo.save(conflict_user)

    headers = {"Authorization": f"Bearer {token}"}
    payload = {"email": "conflict@example.com"}

    response = client.put("/api/v1/usuarios/perfil", json=payload, headers=headers)

    assert response.status_code == 409
    assert "email is already registered" in response.json()["detail"]

