"""Failure and constraint tests for PUT /api/v1/usuarios/perfil."""

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
def failure_setup():
    uow = FakeUnitOfWork()
    user_repo = InMemoryUserRepository()
    persona_repo = InMemoryPersonaRepository()

    persona_id = uuid.uuid4()
    persona = Persona(
        id=persona_id,
        first_name="Test",
        last_name="User",
        identity_card="9988776",
        phone="71234567",
    )
    persona_repo.save(persona)

    user_id = uuid.uuid4()
    # Recently updated: 2 hours ago (< 24 hours)
    recent_time = datetime.now(timezone.utc) - timedelta(hours=2)
    user = User(
        id=user_id,
        persona_id=persona_id,
        email="test.user@example.com",
        password_hash="some_hash",
        role="patient",
        last_profile_update=recent_time,
    )
    user_repo.save(user)

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
        }

    app.dependency_overrides.clear()


def test_update_profile_missing_token():
    """Request without token returns 401 Unauthorized or 403 Forbidden."""
    with TestClient(app) as client:
        response = client.put(
            "/api/v1/usuarios/perfil",
            json={"email": "new@example.com"},
        )
    assert response.status_code in (401, 403)


def test_update_profile_invalid_token(failure_setup):
    """Request with invalid bearer token returns 401 Unauthorized."""
    client = failure_setup["client"]
    headers = {"Authorization": "Bearer invalid.token.payload"}
    response = client.put(
        "/api/v1/usuarios/perfil",
        json={"email": "new@example.com"},
        headers=headers,
    )
    assert response.status_code == 401


def test_update_profile_cooldown_rejection_403(failure_setup):
    """Attempting modification within 24 hours of last update returns 403 Forbidden."""
    client = failure_setup["client"]
    token = failure_setup["token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        "/api/v1/usuarios/perfil",
        json={"email": "new.email@example.com"},
        headers=headers,
    )

    assert response.status_code == 403
    data = response.json()
    assert "Profile modification is locked" in data["detail"]
    assert "remaining" in data["detail"]


def test_update_profile_invalid_email_format(failure_setup):
    """Attempting update with invalid email format returns 422."""
    client = failure_setup["client"]
    token = failure_setup["token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        "/api/v1/usuarios/perfil",
        json={"email": "invalid-email-format"},
        headers=headers,
    )

    assert response.status_code == 422


def test_update_profile_invalid_phone_format(failure_setup):
    """Attempting update with invalid phone format returns 422."""
    client = failure_setup["client"]
    token = failure_setup["token"]

    # Temporarily expire cooldown to test phone validation specifically
    user = failure_setup["user"]
    user.last_profile_update = datetime.now(timezone.utc) - timedelta(hours=25)

    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        "/api/v1/usuarios/perfil",
        json={"phone": "12345678"},  # Must start with 6 or 7
        headers=headers,
    )

    assert response.status_code == 422
    assert "phone" in str(response.json()["detail"])

