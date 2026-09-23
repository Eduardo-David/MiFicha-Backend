"""Failure and Edge-Case tests for user registration."""

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.features.users.presentation.routes import get_ocr_service
from src.features.users.data.mock_ocr_service import MockOCRService


@pytest.fixture
def client():
    app.dependency_overrides[get_ocr_service] = lambda: MockOCRService(should_succeed=True)
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_register_invalid_payload(client):
    payload = {
        "first_name": "Ana",
        # Missing last_name
        "identity_card": "98765432-1A",
        "birth_date": "1995-05-20",
        "phone": "61234567",
        "email": "ana-invalid-email", # Invalid email
        "password": "short", # Short password
        "android_id": "" # Empty android_id
    }

    response = client.post("/api/v1/usuarios", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    
    # We should get multiple validation errors for the missing and invalid fields
    err_msgs = str(data["detail"])
    assert "last_name" in err_msgs
    assert "email" in err_msgs
    assert "password" in err_msgs
    assert "android_id" in err_msgs


def test_register_fails_ocr_verification():
    # Override OCR to fail
    app.dependency_overrides[get_ocr_service] = lambda: MockOCRService(should_succeed=False)
    
    payload = {
        "first_name": "Carlos",
        "last_name": "Mesa",
        "identity_card": "4455667-8C",
        "birth_date": "1980-05-15",
        "phone": "79876543",
        "email": "carlos.mesa.fail@example.com",
        "password": "StrongPassword123!",
        "android_id": "test-device-fail-001"
    }

    with TestClient(app) as client:
        response = client.post("/api/v1/usuarios", json=payload)
        
    assert response.status_code == 422
    assert response.json()["detail"] == "OCR verification failed"
    app.dependency_overrides.clear()
