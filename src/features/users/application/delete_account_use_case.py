"""Delete Account application use case."""

from __future__ import annotations

import uuid
from typing import Any, Dict

from src.features.users.application.exceptions import InvalidCredentialsException
from src.features.users.application.ports import IUnitOfWork
from src.features.users.domain.ports import (
    IDeviceRepository,
    IPasswordHasher,
    IPersonaRepository,
    IUserRepository,
)


class DeleteAccountUseCase:
    """Use case to permanently delete a user account and release resources."""

    def __init__(
        self,
        uow: IUnitOfWork,
        user_repo: IUserRepository,
        persona_repo: IPersonaRepository,
        device_repo: IDeviceRepository,
        password_hasher: IPasswordHasher,
    ) -> None:
        self.uow = uow
        self.user_repo = user_repo
        self.persona_repo = persona_repo
        self.device_repo = device_repo
        self.password_hasher = password_hasher

    def execute(self, user_id: uuid.UUID, password: str) -> Dict[str, str]:
        """Execute the account deletion workflow.

        Args:
            user_id: ID of the user requesting deletion.
            password: Password challenge for security verification.

        Returns:
            Success confirmation message.

        Raises:
            InvalidCredentialsException: If user not found or password incorrect.
        """
        user = self.user_repo.find_by_id(user_id)
        if user is None:
            raise InvalidCredentialsException("User not found")

        # 1. Challenge password verification
        if not self.password_hasher.verify(password, user.password_hash):
            raise InvalidCredentialsException("Invalid password challenge")

        persona_id = user.persona_id

        # 2. Atomic deletion and asset release
        with self.uow:
            self.device_repo.delete_by_user_id(user.id)
            self.user_repo.delete(user.id)
            self.persona_repo.delete(persona_id)
            self.uow.commit()

        return {
            "message": "Cuenta eliminada exitosamente. Se ha desvinculado el dispositivo y liberado la identidad."
        }

