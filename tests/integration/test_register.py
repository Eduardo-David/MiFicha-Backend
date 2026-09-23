"""Integration tests for user registration."""

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.features.users.application.ports import IOCRService
from src.features.users.presentation.routes import get_ocr_service
from src.features.users.data.mock_ocr_service import MockOCRService


@pytest.fixture
def client():
    # Override OCR service to always succeed for happy path tests
    app.dependency_overrides[get_ocr_service] = lambda: MockOCRService(should_succeed=True)
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_register_user_success(client):
    payload = {
        "first_name": "Carlos",
        "last_name": "Mesa",
        "identity_card": "4455667-8C",
        "birth_date": "1980-05-15",
        "phone": "79876543",
        "email": "carlos.mesa.test@example.com",
        "password": "StrongPassword123!",
        "android_id": "test-device-integration-001"
    }

    response = client.post("/api/v1/usuarios", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["email"] == "carlos.mesa.test@example.com"
    assert data["role"] == "patient"


def test_register_user_duplicate_email(client):
    payload = {
        "first_name": "Carlos",
        "last_name": "Mesa",
        "identity_card": "4455667-9D", # Different CI
        "birth_date": "1980-05-15",
        "phone": "79876543",
        "email": "carlos.mesa.test@example.com", # Same email
        "password": "StrongPassword123!",
        "android_id": "test-device-integration-002" # Different device
    }

    response = client.post("/api/v1/usuarios", json=payload)
    assert response.status_code == 409
    assert response.json()["detail"] == "email is already registered"
