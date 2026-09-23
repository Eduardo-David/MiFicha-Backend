"""Integration tests for user authentication and JWT token issuance."""

import uuid
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.features.users.domain.models import User
from src.features.users.domain.ports import IUserRepository
from src.features.users.presentation.routes import get_user_repository
from src.features.users.data.auth.bcrypt_hasher import BcryptPasswordHasher
from src.features.users.data.auth.jwt_service import PyJWTTokenService


class InMemoryUserRepository(IUserRepository):
    """In-memory user repository for isolated integration tests."""

    def __init__(self):
        self.users = {}

    def save(self, user: User) -> None:
        self.users[user.email] = user

    def find_by_id(self, user_id: uuid.UUID):
        for user in self.users.values():
            if user.id == user_id:
                return user
        return None

    def find_by_email(self, email: str):
        return self.users.get(email)

    def delete(self, user_id: uuid.UUID) -> None:
        for email, user in list(self.users.items()):
            if user.id == user_id:
                del self.users[email]


@pytest.fixture
def user_repo():
    """Fixture providing an isolated user repository with a registered test user."""
    repo = InMemoryUserRepository()
    hasher = BcryptPasswordHasher()
    hashed_password = hasher.hash("SecurePass123")

    test_user = User(
        id=uuid.uuid4(),
        persona_id=uuid.uuid4(),
        email="patient@mificha.com",
        password_hash=hashed_password,
        role="patient",
    )
    repo.save(test_user)
    return repo


@pytest.fixture
def client(user_repo):
    """Fixture providing TestClient with overridden user repository dependency."""
    app.dependency_overrides[get_user_repository] = lambda: user_repo
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_successful_login(client, user_repo):
    """Scenario: Successful login with valid credentials (BDD Scenario 1)."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "patient@mificha.com", "password": "SecurePass123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Verify the emitted token is valid and properly signed
    token_service = PyJWTTokenService()
    payload = token_service.verify_token(data["access_token"])

    test_user = user_repo.find_by_email("patient@mificha.com")
    assert payload["sub"] == str(test_user.id)
    assert "exp" in payload

    # Verify token expires in ~15 minutes (within a reasonable window)
    now_ts = datetime.now(timezone.utc).timestamp()
    exp_diff = payload["exp"] - now_ts
    assert 14 * 60 < exp_diff <= 15 * 60 + 5


def test_failed_login_with_incorrect_password(client):
    """Scenario: Failed login with incorrect password (BDD Scenario 2)."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "patient@mificha.com", "password": "WrongPassword"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect email or password"}


def test_rejection_of_short_password(client):
    """Scenario: Rejection of malformed input - password too short (BDD Scenario 4)."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "patient@mificha.com", "password": "short"},
    )

    assert response.status_code == 422
    errors = response.json().get("detail", [])
    assert any(err["loc"][-1] == "password" for err in errors)


def test_rejection_of_invalid_email_format(client):
    """Scenario: Rejection of malformed input - invalid email format (BDD Scenario 4)."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "not-an-email", "password": "SecurePass123"},
    )

    assert response.status_code == 422
    errors = response.json().get("detail", [])
    assert any(err["loc"][-1] == "email" for err in errors)
