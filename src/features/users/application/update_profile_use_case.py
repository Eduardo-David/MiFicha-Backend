"""Update Profile application use case."""

from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from src.features.users.application.exceptions import (
    EntityAlreadyExistsException,
    InvalidCredentialsException,
)
from src.features.users.application.ports import IUnitOfWork
from src.features.users.domain.exceptions import ValidationError
from src.features.users.domain.ports import IPersonaRepository, IUserRepository

_PHONE_REGEX = re.compile(r"^[67]\d{7}$")


class UpdateProfileUseCase:
    """Use case to update user profile with 24-hour cooldown enforcement."""

    def __init__(
        self,
        uow: IUnitOfWork,
        user_repo: IUserRepository,
        persona_repo: IPersonaRepository,
    ) -> None:
        self.uow = uow
        self.user_repo = user_repo
        self.persona_repo = persona_repo

    def execute(
        self,
        user_id: uuid.UUID,
        new_email: Optional[str] = None,
        new_phone: Optional[str] = None,
        current_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Execute profile update workflow.

        Args:
            user_id: ID of the authenticated user.
            new_email: New email address (optional).
            new_phone: New Bolivian phone number (optional).
            current_time: Optional time override for testing.

        Returns:
            Dictionary containing updated profile information.

        Raises:
            InvalidCredentialsException: If user not found.
            EntityAlreadyExistsException: If new_email is already taken.
            RestriccionTiempoException: If 24-hour cooldown has not expired.
            ValidationError: If email or phone format is invalid.
        """
        user = self.user_repo.find_by_id(user_id)
        if user is None:
            raise InvalidCredentialsException("User not found")

        # 1. Uniqueness check for email
        if new_email and new_email != user.email:
            existing = self.user_repo.find_by_email(new_email)
            if existing is not None and existing.id != user.id:
                raise EntityAlreadyExistsException("email", "Email already registered")

        persona = self.persona_repo.find_by_id(user.persona_id)

        # 2. Validate phone if provided
        if new_phone is not None:
            if not _PHONE_REGEX.match(new_phone):
                raise ValidationError(
                    "phone must be a valid Bolivian number: start with 6 or 7, 8 digits, numbers only",
                    field="phone",
                )

        # 3. Domain invariant enforcement (including 24-hour cooldown)
        user.update_profile(new_email=new_email, current_time=current_time)
        if new_phone is not None and persona is not None:
            persona.phone = new_phone

        # 4. Atomic persistence
        with self.uow:
            self.user_repo.save(user)
            if persona is not None:
                self.persona_repo.save(persona)
            self.uow.commit()

        return {
            "id": str(user.id),
            "email": user.email,
            "phone": persona.phone if persona else None,
            "last_profile_update": user.last_profile_update.isoformat(),
        }

