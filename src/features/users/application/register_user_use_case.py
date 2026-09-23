"""Registration application use case."""

from __future__ import annotations

from typing import Dict, Any

from src.features.users.application.exceptions import (
    EntityAlreadyExistsException,
    OCRVerificationFailedException,
)
from src.features.users.application.ports import IOCRService, IUnitOfWork
from src.features.users.domain.ports import (
    IPasswordHasher,
    IPersonaRepository,
    IUserRepository,
    IDeviceRepository,
)
from src.features.users.domain.models import Persona, User, Device


class RegisterUserUseCase:
    """Use case to register a new user account with OCR validation and device binding."""

    def __init__(
        self,
        uow: IUnitOfWork,
        persona_repo: IPersonaRepository,
        user_repo: IUserRepository,
        device_repo: IDeviceRepository,
        password_hasher: IPasswordHasher,
        ocr_service: IOCRService,
    ) -> None:
        self.uow = uow
        self.persona_repo = persona_repo
        self.user_repo = user_repo
        self.device_repo = device_repo
        self.password_hasher = password_hasher
        self.ocr_service = ocr_service

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the registration workflow.

        Args:
            data: Dictionary containing registration fields.

        Returns:
            Dictionary with registered user details: id, email, role.

        Raises:
            EntityAlreadyExistsException: If uniqueness constraint is violated.
            OCRVerificationFailedException: If OCR validation fails.
            ValidationError: If domain invariant validation fails.
        """
        # 1. OCR Validation
        is_valid_identity = self.ocr_service.verify_identity(
            identity_card=data["identity_card"],
            first_name=data["first_name"],
            last_name=data["last_name"],
        )
        if not is_valid_identity:
            raise OCRVerificationFailedException()

        # 2. Check for uniqueness before transaction
        if self.persona_repo.find_by_identity_card(data["identity_card"]):
            raise EntityAlreadyExistsException("identity_card", "Identity card already registered")
        
        if self.user_repo.find_by_email(data["email"]):
            raise EntityAlreadyExistsException("email", "Email already registered")
            
        if self.device_repo.find_by_android_id(data["android_id"]):
            raise EntityAlreadyExistsException("android_id", "Device already registered")

        # 3. Hash password
        hashed_password = self.password_hasher.hash(data["password"])

        # 4. Build domain entities
        persona = Persona(
            first_name=data["first_name"],
            last_name=data["last_name"],
            identity_card=data["identity_card"],
            birth_date=data.get("birth_date"),
            email=data["email"],
            phone=data["phone"],
        )
        
        user = User(
            persona_id=persona.id,
            email=data["email"],
            password_hash=hashed_password,
            role="patient"
        )
        
        device = Device(
            user_id=user.id,
            android_id=data["android_id"]
        )

        # 5. Persist atomically
        with self.uow:
            self.persona_repo.save(persona)
            self.user_repo.save(user)
            self.device_repo.save(device)
            self.uow.commit()

        # 6. Return response DTO
        return {
            "id": str(user.id),
            "email": user.email,
            "role": user.role,
        }
