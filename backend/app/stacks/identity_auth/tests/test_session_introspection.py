import pytest
from unittest.mock import AsyncMock, MagicMock

from backend.app.stacks.identity_auth.session_introspection import get_session_introspection
from backend.app.stacks.identity_auth.models import IdentityUser


@pytest.mark.asyncio
async def test_session_introspection_with_display_name():
    """Test that session introspection returns display name."""
    # Mock repository
    mock_repo = AsyncMock()

    # Create a user with display name
    mock_user = MagicMock(spec=IdentityUser)
    mock_user.id = "test-user-id"
    mock_user.role = "user"
    mock_user.subscription_tier = "free"
    mock_user.is_active = True
    mock_user.status = "active"
    mock_user.must_change_password = False
    mock_user.display_name = "John Doe"
    mock_user.email_normalized = "test@example.com"

    mock_repo.get_by_id.return_value = mock_user

    # Test introspection
    result = await get_session_introspection("test-user-id", mock_repo)

    assert result["user_id"] == "test-user-id"
    assert result["role"] == "user"
    assert result["subscription_tier"] == "free"
    assert result["status"] == "active"
    assert result["is_active"] == True
    assert result["must_change_password"] == False
    assert result["display_name"] == "John Doe"
    assert result["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_session_introspection_without_display_name():
    """Test that session introspection works with None display name."""
    # Mock repository
    mock_repo = AsyncMock()

    # Create a user without display name
    mock_user = MagicMock(spec=IdentityUser)
    mock_user.id = "test-user-id"
    mock_user.role = "user"
    mock_user.subscription_tier = "free"
    mock_user.is_active = True
    mock_user.status = "active"
    mock_user.must_change_password = False
    mock_user.display_name = None
    mock_user.email_normalized = "test@example.com"

    mock_repo.get_by_id.return_value = mock_user

    # Test introspection
    result = await get_session_introspection("test-user-id", mock_repo)

    assert result["display_name"] is None
    assert result["email"] == "test@example.com"
