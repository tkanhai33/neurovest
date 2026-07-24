import pytest
from unittest.mock import AsyncMock, MagicMock

from backend.app.stacks.identity_auth.api_models import (
    RegistrationApiRequest,
    LoginApiRequest,
)
from backend.app.stacks.identity_auth.service_contracts import (
    AuthenticationTokenPair,
    LoginCommand,
    RegistrationCommand,
    RegisteredIdentity,
)


@pytest.mark.asyncio
async def test_registration_api_with_display_name():
    """Test that registration API accepts display name in request."""
    # This is a basic test to ensure the model accepts display_name field
    request = RegistrationApiRequest(
        email="test@example.com",
        password="securepassword123",
        display_name="John Doe"
    )

    assert request.email == "test@example.com"
    assert request.password == "securepassword123"
    assert request.display_name == "John Doe"


@pytest.mark.asyncio
async def test_registration_api_without_display_name():
    """Test that registration API works without display name."""
    # This is a basic test to ensure the model accepts None for display_name
    request = RegistrationApiRequest(
        email="test@example.com",
        password="securepassword123"
    )

    assert request.email == "test@example.com"
    assert request.password == "securepassword123"
    assert request.display_name is None


@pytest.mark.asyncio
async def test_login_api_request():
    """Test that login API request model works correctly."""
    request = LoginApiRequest(
        email="test@example.com",
        password="securepassword123"
    )

    assert request.email == "test@example.com"
    assert request.password == "securepassword123"
