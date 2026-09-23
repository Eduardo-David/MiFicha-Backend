"""Unit tests for the Registration Use Case."""

import uuid
import pytest
from datetime import date
from typing import Optional

from src.features.users.application.register_user_use_case import RegisterUserUseCase
from src.features.users.application.exceptions import (
    EntityAlreadyExistsException,
    OCRVerificationFailedException,
)
from src.features.users.domain.ports import (
    IPersonaRepository,
    IUserRepository,
    IDeviceRepository,
)
from src.features.users.domain.models import Persona, User, Device
from src.features.users.application.ports import IUnitOfWork
from src.features.users.data.auth.bcrypt_hasher import BcryptPasswordHasher
from src.features.users.data.mock_ocr_service import MockOCRService


class InMemoryPersonaRepository(IPersonaRepository):
    def __init__(self):
        self.personas = {}
    def save(self, persona: Persona) -> None:
        self.personas[persona.id] = persona
    def find_by_id(self, persona_id: uuid.UUID) -> Optional[Persona]:
        return self.personas.get(persona_id)
    def find_by_identity_card(self, identity_card: str) -> Optional[Persona]:
        for p in self.personas.values():
            if p.identity_card == identity_card:
                return p
        return None


class InMemoryUserRepository(IUserRepository):
    def __init__(self):
        self.users = {}
    def save(self, user: User) -> None:
        self.users[user.id] = user
    def find_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        return self.users.get(user_id)
    def find_by_email(self, email: str) -> Optional[User]:
        for u in self.users.values():
            if u.email == email:
                return u
        return None
    def delete(self, user_id: uuid.UUID) -> None:
        if user_id in self.users:
            del self.users[user_id]


class InMemoryDeviceRepository(IDeviceRepository):
    def __init__(self):
        self.devices = {}
    def save(self, device: Device) -> None:
        self.devices[device.id] = device
    def find_by_android_id(self, android_id: str) -> Optional[Device]:
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
def register_use_case():
    return RegisterUserUseCase(
        uow=FakeUnitOfWork(),
        persona_repo=InMemoryPersonaRepository(),
        user_repo=InMemoryUserRepository(),
        device_repo=InMemoryDeviceRepository(),
        password_hasher=BcryptPasswordHasher(),
        ocr_service=MockOCRService(should_succeed=True),
    )


def test_register_user_success(register_use_case):
    data = {
        "first_name": "Ana",
        "last_name": "Gomez",
        "identity_card": "98765432-1A",
        "birth_date": date(1995, 5, 20),
        "phone": "61234567",
        "email": "ana@example.com",
        "password": "SecurePassword123",
        "android_id": "test-android-123"
    }
    result = register_use_case.execute(data)
    
    assert "id" in result
    assert result["email"] == "ana@example.com"
    assert result["role"] == "patient"
    assert register_use_case.uow.committed is True


def test_register_user_fails_ocr():
    ocr_service = MockOCRService(should_succeed=False)
    use_case = RegisterUserUseCase(
        uow=FakeUnitOfWork(),
        persona_repo=InMemoryPersonaRepository(),
        user_repo=InMemoryUserRepository(),
        device_repo=InMemoryDeviceRepository(),
        password_hasher=BcryptPasswordHasher(),
        ocr_service=ocr_service,
    )
    
    data = {
        "first_name": "Ana",
        "last_name": "Gomez",
        "identity_card": "98765432-1A",
        "phone": "61234567",
        "email": "ana@example.com",
        "password": "SecurePassword123",
        "android_id": "test-android-123"
    }
    with pytest.raises(OCRVerificationFailedException):
        use_case.execute(data)
