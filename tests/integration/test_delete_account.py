"""Integration tests for user account deletion (DELETE /api/v1/usuarios/cuenta)."""

import uuid
import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.features.users.application.ports import IUnitOfWork
from src.features.users.domain.models import Device, Persona, User
from src.features.users.domain.ports import (
    IDeviceRepository,
    IPasswordHasher,
    IPersonaRepository,
    IUserRepository,
)
from src.features.users.data.auth.bcrypt_hasher import BcryptPasswordHasher
from src.features.users.data.auth.jwt_service import PyJWTTokenService
from src.features.users.presentation.routes import (
    get_device_repository,
    get_password_hasher,
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


class InMemoryDeviceRepository(IDeviceRepository):
    def __init__(self):
        self.devices = {}

    def save(self, device: Device) -> None:
        self.devices[device.id] = device

    def find_by_android_id(self, android_id: str):
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
def delete_setup():
    hasher = BcryptPasswordHasher()
    hashed = hasher.hash("SecretPassword123")

    uow = FakeUnitOfWork()
    user_repo = InMemoryUserRepository()
    persona_repo = InMemoryPersonaRepository()
    device_repo = InMemoryDeviceRepository()

    persona = Persona(
        id=uuid.uuid4(),
        first_name="Patricia",
        last_name="Flores",
        identity_card="6543210-9X",
        phone="71234567",
    )
    persona_repo.save(persona)

    user = User(
        id=uuid.uuid4(),
        persona_id=persona.id,
        email="patricia.flores@example.com",
        password_hash=hashed,
        role="patient",
    )
    user_repo.save(user)

    device = Device(
        id=uuid.uuid4(),
        user_id=user.id,
        android_id="android-patricia-hardware-id",
    )
    device_repo.save(device)

    token_service = PyJWTTokenService()
    token = token_service.create_access_token({"sub": str(user.id)})

    app.dependency_overrides[get_user_repository] = lambda: user_repo
    app.dependency_overrides[get_persona_repository] = lambda: persona_repo
    app.dependency_overrides[get_device_repository] = lambda: device_repo
    app.dependency_overrides[get_password_hasher] = lambda: hasher
    app.dependency_overrides[get_unit_of_work] = lambda: uow

    with TestClient(app) as test_client:
        yield {
            "client": test_client,
            "token": token,
            "user": user,
            "persona": persona,
            "device": device,
            "user_repo": user_repo,
            "persona_repo": persona_repo,
            "device_repo": device_repo,
        }

    app.dependency_overrides.clear()


def test_delete_account_success(delete_setup):
    """DELETE /api/v1/usuarios/cuenta successfully deletes account and releases resources."""
    client = delete_setup["client"]
    token = delete_setup["token"]
    user = delete_setup["user"]
    persona = delete_setup["persona"]
    device = delete_setup["device"]
    user_repo = delete_setup["user_repo"]
    persona_repo = delete_setup["persona_repo"]
    device_repo = delete_setup["device_repo"]

    headers = {"Authorization": f"Bearer {token}"}
    payload = {"password": "SecretPassword123"}

    response = client.request("DELETE", "/api/v1/usuarios/cuenta", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "Cuenta eliminada exitosamente" in data["message"]
    assert "liberado la identidad" in data["message"]

    # Verify complete cleanup across repositories
    assert user_repo.find_by_id(user.id) is None
    assert persona_repo.find_by_id(persona.id) is None
    assert persona_repo.find_by_identity_card(persona.identity_card) is None
    assert device_repo.find_by_android_id(device.android_id) is None

