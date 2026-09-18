"""Pure domain entities for User Management.

Zero external dependencies: only Python standard library.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from .exceptions import RestriccionTiempoException, ValidationError


# Module-level compiled regex patterns for performance
_EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_IDENTITY_CARD_REGEX = re.compile(r"^[A-Za-z0-9]{5,}(-[A-Za-z0-9]+)?$")
_PHONE_REGEX = re.compile(r"^[67]\d{7}$")

_VALID_ROLES = {"dev", "admin", "doctor", "patient"}


def _generate_uuid() -> uuid.UUID:
    """Factory for UUID generation (allows mocking in tests)."""
    return uuid.uuid4()


@dataclass(slots=True)
class Persona:
    """Represents the physical identity of a human.

    Invariants:
    - identity_card: alphanumeric, min 5 chars, optional hyphen + alphanumeric extension
    - email: RFC-compliant pattern (contains @ and valid domain with dot)
    - phone: Bolivian format - starts with 6 or 7, 8 digits, numbers only
    """

    id: uuid.UUID = field(default_factory=_generate_uuid)
    first_name: str = ""
    last_name: str = ""
    identity_card: str = ""
    email: str = ""
    phone: str = ""

    def __post_init__(self) -> None:
        """Validate all invariants on construction."""
        self._validate_identity_card()
        self._validate_email()
        self._validate_phone()

    def _validate_identity_card(self) -> None:
        if not self.identity_card:
            raise ValidationError("identity_card cannot be empty", field="identity_card")
        if not _IDENTITY_CARD_REGEX.match(self.identity_card):
            raise ValidationError(
                "identity_card must be alphanumeric (min 5 chars), "
                "optional hyphen followed by alphanumeric extension",
                field="identity_card",
            )

    def _validate_email(self) -> None:
        if not self.email:
            raise ValidationError("email cannot be empty", field="email")
        if not _EMAIL_REGEX.match(self.email):
            raise ValidationError(
                "email must contain @ and a valid domain with a dot",
                field="email",
            )

    def _validate_phone(self) -> None:
        if not self.phone:
            raise ValidationError("phone cannot be empty", field="phone")
        if not _PHONE_REGEX.match(self.phone):
            raise ValidationError(
                "phone must be a valid Bolivian number: "
                "start with 6 or 7, 8 digits, numbers only",
                field="phone",
            )


@dataclass(slots=True)
class User:
    """Represents the system credentials, security state, and access permissions.

    Behavior (Information Expert):
    - update_profile: enforces 24-hour cooldown on profile modifications
    """

    id: uuid.UUID = field(default_factory=_generate_uuid)
    persona_id: uuid.UUID = field(default_factory=_generate_uuid)
    email: str = ""
    password_hash: str = ""
    role: str = ""
    last_profile_update: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate role on construction."""
        self._validate_role()

    def _validate_role(self) -> None:
        if not self.role:
            raise ValidationError("role cannot be empty", field="role")
        if self.role not in _VALID_ROLES:
            raise ValidationError(
                f"role must be one of: {', '.join(sorted(_VALID_ROLES))}",
                field="role",
            )

    def update_profile(self, new_email: str, current_time: datetime) -> None:
        """Update user's email with 24-hour cooldown enforcement.

        Args:
            new_email: The new email address to set.
            current_time: Current UTC time (timezone-naive).

        Raises:
            ValidationError: If new_email is invalid.
            RestriccionTiempoException: If less than 24 hours have passed
                since last_profile_update.
        """
        # Validate new email format
        if not new_email:
            raise ValidationError("email cannot be empty", field="email")
        if not _EMAIL_REGEX.match(new_email):
            raise ValidationError(
                "email must contain @ and a valid domain with a dot",
                field="email",
            )

        # 24-hour cooldown validation
        elapsed = current_time - self.last_profile_update
        cooldown = timedelta(hours=24)

        if elapsed < cooldown:
            remaining = cooldown - elapsed
            raise RestriccionTiempoException(time_remaining=remaining)

        # Update allowed
        self.email = new_email
        self.last_profile_update = current_time


@dataclass(slots=True)
class Device:
    """Represents a physical mobile terminal bound to a user account."""

    id: uuid.UUID = field(default_factory=_generate_uuid)
    user_id: uuid.UUID = field(default_factory=_generate_uuid)
    android_id: str = ""