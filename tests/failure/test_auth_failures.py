"""Security failure & timing-attack tests for authentication flow."""

from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.users.application.exceptions import InvalidTokenException
from src.users.application.login_use_case import _DUMMY_BCRYPT_HASH
from src.users.domain.ports import IUserRepository
from src.users.infrastructure.api.routes import get_password_hasher, get_user_repository
from src.users.infrastructure.auth.bcrypt_hasher import BcryptPasswordHasher
from src.users.infrastructure.auth.jwt_service import PyJWTTokenService


class EmptyUserRepository(IUserRepository):
    """Empty repository simulating non-existent users in database."""

    def save(self, user):
        pass

    def find_by_id(self, user_id):
        return None

    def find_by_email(self, email):
        return None

    def delete(self, user_id):
        pass


def test_login_non_existent_email_triggers_dummy_bcrypt_check():
    """Scenario: Non-existent email triggers anti-timing dummy check (BDD Scenario 3)."""
    empty_repo = EmptyUserRepository()
    real_hasher = BcryptPasswordHasher()

    # Wrap real hasher in a mock spy to observe calls
    hasher_spy = MagicMock(wraps=real_hasher)

    app.dependency_overrides[get_user_repository] = lambda: empty_repo
    app.dependency_overrides[get_password_hasher] = lambda: hasher_spy

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/auth/login",
                json={"email": "unknown@mificha.com", "password": "SecurePass123"},
            )

        assert response.status_code == 401
        assert response.json() == {"detail": "Incorrect email or password"}

        # Verify that dummy check was executed to guarantee constant execution time
        assert hasher_spy.verify.called
        call_args = hasher_spy.verify.call_args[0]
        assert call_args[0] == "SecurePass123"
        assert call_args[1] == _DUMMY_BCRYPT_HASH
    finally:
        app.dependency_overrides.clear()


def test_token_service_rejects_expired_token():
    """Verify that expired tokens fail validation with InvalidTokenException."""
    token_service = PyJWTTokenService(expire_minutes=-5)
    expired_token = token_service.create_access_token({"sub": "user-123"})

    verifier_service = PyJWTTokenService()
    with pytest.raises(InvalidTokenException):
        verifier_service.verify_token(expired_token)


def test_token_service_rejects_invalid_signature():
    """Verify that tokens signed with a different key are rejected."""
    token_service = PyJWTTokenService(secret_key="attacker-secret-key-123456789012")
    forged_token = token_service.create_access_token({"sub": "user-123"})

    verifier_service = PyJWTTokenService()
    with pytest.raises(InvalidTokenException):
        verifier_service.verify_token(forged_token)


def test_token_service_rejects_malformed_token():
    """Verify that malformed or garbage strings are rejected as invalid tokens."""
    verifier_service = PyJWTTokenService()
    with pytest.raises(InvalidTokenException):
        verifier_service.verify_token("invalid.jwt.token.string")
