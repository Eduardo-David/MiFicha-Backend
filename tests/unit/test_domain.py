"""Unit tests for User Management domain entities.

Tests verify pure domain logic in absolute isolation (no mocks needed).
"""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from src.users.domain.exceptions import (
    RestriccionTiempoException,
    ValidationError,
)
from src.users.domain.models import Device, Persona, User


class TestPersona:
    """Tests for Persona entity (Bolivian validations)."""

    def test_valid_persona_creation(self):
        """Scenario 1: Successful initialization with valid Bolivian data."""
        persona = Persona(
            first_name="Juan",
            last_name="Perez",
            identity_card="6543210-2A",
            phone="71234567",
        )

        assert persona.first_name == "Juan"
        assert persona.last_name == "Perez"
        assert persona.identity_card == "6543210-2A"
        assert persona.phone == "71234567"
        assert isinstance(persona.id, uuid4().__class__)

    def test_valid_persona_without_extension(self):
        """Identity card without hyphen extension should be valid."""
        persona = Persona(
            first_name="Maria",
            last_name="Gonzalez",
            identity_card="12345678",
            phone="61234567",
        )
        assert persona.identity_card == "12345678"

    @pytest.mark.parametrize(
        "invalid_phone,description",
        [
            ("81234567", "starts with 8 (invalid prefix)"),
            ("7123456", "length 7 (too short)"),
            ("712345678", "length 9 (too long)"),
            ("7abcdefg", "contains letters"),
            ("7123-456", "contains hyphen"),
            ("", "empty string"),
        ],
    )
    def test_invalid_phone_raises_validation_error(
        self, invalid_phone: str, description: str
    ):
        """Scenario 2: Validation rejection on invalid Bolivian phone format."""
        with pytest.raises(ValidationError) as exc_info:
            Persona(
                first_name="Test",
                last_name="User",
                identity_card="1234567",
                phone=invalid_phone,
            )
        assert exc_info.value.field == "phone"

    @pytest.mark.parametrize(
        "invalid_ic,description",
        [
            ("", "empty string"),
            ("1234", "length 4 (< 5 min)"),
            ("1234-", "ends with hyphen, no extension"),
            ("1234-AB!", "contains special character !"),
            ("12-34-56", "multiple hyphens"),
            ("abcd", "length 4, no hyphen"),
        ],
    )
    def test_invalid_identity_card_raises_validation_error(
        self, invalid_ic: str, description: str
    ):
        """Scenario 3: Validation rejection on invalid identity card format."""
        with pytest.raises(ValidationError) as exc_info:
            Persona(
                first_name="Test",
                last_name="User",
                identity_card=invalid_ic,
                phone="71234567",
            )
        assert exc_info.value.field == "identity_card"

class TestUser:
    """Tests for User entity (24-hour cooldown logic)."""

    def test_valid_user_creation(self):
        """User can be created with valid role."""
        user = User(
            persona_id=uuid4(),
            email="user@example.com",
            password_hash="hashed_password",
            role="patient",
        )
        assert user.role == "patient"
        assert isinstance(user.last_profile_update, datetime)

    @pytest.mark.parametrize("invalid_role", ["superadmin", "nurse", "", "PATIENT"])
    def test_invalid_role_raises_validation_error(self, invalid_role: str):
        """Role must be one of the allowed values."""
        with pytest.raises(ValidationError) as exc_info:
            User(
                persona_id=uuid4(),
                email="user@example.com",
                password_hash="hashed",
                role=invalid_role,
            )
        assert exc_info.value.field == "role"

    def test_update_profile_blocked_within_24_hours(self):
        """Scenario 4: Profile modification blocked within 24-hour lock period."""
        # Given: last_profile_update = 2026-09-06 12:00:00
        last_update = datetime(2026, 9, 6, 12, 0, 0)
        user = User(
            persona_id=uuid4(),
            email="old@example.com",
            password_hash="hashed",
            role="patient",
            last_profile_update=last_update,
        )

        # When: request at 2026-09-06 18:00:00 (only 6 hours elapsed)
        request_time = datetime(2026, 9, 6, 18, 0, 0)

        # Then: RestriccionTiempoException with 18 hours remaining
        with pytest.raises(RestriccionTiempoException) as exc_info:
            user.update_profile(new_email="new@mificha.com", current_time=request_time)

        assert exc_info.value.time_remaining == timedelta(hours=18)
        assert "18h 0m" in str(exc_info.value)
        # Email should NOT be updated
        assert user.email == "old@example.com"
        assert user.last_profile_update == last_update

    def test_update_profile_allowed_after_24_hours(self):
        """Scenario 5: Profile modification allowed after 24-hour lock period."""
        # Given: last_profile_update = 2026-09-06 12:00:00
        last_update = datetime(2026, 9, 6, 12, 0, 0)
        user = User(
            persona_id=uuid4(),
            email="old@example.com",
            password_hash="hashed",
            role="patient",
            last_profile_update=last_update,
        )

        # When: request at 2026-09-07 13:00:00 (25 hours elapsed)
        request_time = datetime(2026, 9, 7, 13, 0, 0)
        user.update_profile(new_email="new@mificha.com", current_time=request_time)

        # Then: email updated, last_profile_update updated
        assert user.email == "new@mificha.com"
        assert user.last_profile_update == request_time

    def test_update_profile_exactly_24_hours_allowed(self):
        """Edge case: exactly 24 hours should be allowed."""
        last_update = datetime(2026, 9, 6, 12, 0, 0)
        user = User(
            persona_id=uuid4(),
            email="old@example.com",
            password_hash="hashed",
            role="patient",
            last_profile_update=last_update,
        )

        # Exactly 24 hours later
        request_time = datetime(2026, 9, 7, 12, 0, 0)
        user.update_profile(new_email="new@example.com", current_time=request_time)

        assert user.email == "new@example.com"
        assert user.last_profile_update == request_time

    def test_update_profile_invalid_email_raises_validation_error(self):
        """update_profile validates new email format."""
        last_update = datetime(2026, 9, 6, 12, 0, 0)
        user = User(
            persona_id=uuid4(),
            email="old@example.com",
            password_hash="hashed",
            role="patient",
            last_profile_update=last_update,
        )

        request_time = datetime(2026, 9, 7, 13, 0, 0)  # After cooldown

        with pytest.raises(ValidationError) as exc_info:
            user.update_profile(new_email="invalid-email", current_time=request_time)

        assert exc_info.value.field == "email"
        # Original email unchanged
        assert user.email == "old@example.com"


class TestDevice:
    """Tests for Device entity."""

    def test_device_creation(self):
        """Device can be created with required fields."""
        user_id = uuid4()
        device = Device(user_id=user_id, android_id="android123unique")

        assert device.user_id == user_id
        assert device.android_id == "android123unique"
        assert isinstance(device.id, uuid4().__class__)