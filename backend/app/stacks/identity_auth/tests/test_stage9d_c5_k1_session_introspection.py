from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.main import app
from backend.app.stacks.identity_auth.api_models import (
    LoginApiRequest,
)
from backend.app.stacks.identity_auth.repositories import IdentityUserRepository


@pytest.mark.asyncio
async def test_session_introspection(
    client: TestClient, async_session: AsyncSession
):
    # Create a test user
    user_repo = IdentityUserRepository(async_session)
    user = await user_repo.create(
        email="test@example.com",
        password_hash="hashed_password",
        role="user",
        must_change_password=False,
    )

    # Log in to get an access token
    login_request = LoginApiRequest(
        email=user.email_normalized, password="password"
    )
    response = client.post("/auth/login", json=login_request.dict())
    assert response.status_code == 200
    access_token = response.json().get("access_token")

    # Introspect the session
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/auth/introspection", headers=headers)
    assert response.status_code == 200

    introspection_data = response.json()
    assert "user_id" in introspection_data
    assert "role" in introspection_data
    assert "subscription_tier" in introspection_data
    assert "permissions" in introspection_data
    assert "is_administrative" in introspection_data
    assert "status" in introspection_data
    assert "is_active" in introspection_data
    assert "must_change_password" in introspection_data

    # Clean up the test user
    await user_repo.delete(user.id)
