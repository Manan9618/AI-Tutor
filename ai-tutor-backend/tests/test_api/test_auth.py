# tests/test_api/test_auth.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_and_login(async_client, db_session):
    """
    Test user registration and login flow via Auth API.
    """
    # --- Register user ---
    register_payload = {
        "username": "testuser",
        "password": "testpass123",
        "email": "test@example.com"
    }

    response = await async_client.post("/api/auth/register", json=register_payload)
    assert response.status_code in (200, 201)
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # --- Login user ---
    login_payload = {
        "username": "testuser",
        "password": "testpass123"
    }

    response = await async_client.post("/api/auth/token", data=login_payload)
    assert response.status_code == 200
    token_data = response.json()

    assert "access_token" in token_data
    token = token_data["access_token"]
    assert isinstance(token, str)
    assert token.startswith("ey")  # typical JWT structure
