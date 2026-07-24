import pytest
from unittest.mock import AsyncMock, MagicMock

from backend.app.stacks.identity_auth.api_models import (
    RegistrationApiRequest,
)
from backend.app.stacks.identity_auth.registration_service import (
    RegistrationService,
)
from backend.app.stacks.identity_auth.repositories import IdentityUserRepository
from backend.app.stacks.identity_auth.service_contracts import (
    RegistrationCommand,
    RegistrationRejectedError,
)


@pytest.mark.asyncio
async def test_registration_with_display_name():
    """Test that registration accepts and stores a display name."""
    # Mock dependencies
    mock_user_repo = AsyncMock(spec=IdentityUserRepository)
    mock_user_repo.get_by_email.return_value = None
    mock_hash_password = MagicMock(return_value="hashed_password")
    mock_commit = AsyncMock()
    mock_rollback = AsyncMock()

    # Create service
    service = RegistrationService(
        user_repository=mock_user_repo,
        hash_password=mock_hash_password,
        commit=mock_commit,
        rollback=mock_rollback,
    )

    # Mock the repository to return None for existing user (not found)
    mock_user_repo.get_by_email.return_value = None

    # Mock the repository create method
    mock_user = MagicMock()
    mock_user.id = "test-user-id"
    mock_user.email_normalized = "test@example.com"
    mock_user.status = "active"
    mock_user_repo.create.return_value = mock_user

    # Test registration with display name
    command = RegistrationCommand(
        email="test@example.com",
        password="securepassword123",
        display_name="John Doe"
    )

    result = await service.register(command)

    # Verify that create was called with the display name
    mock_user_repo.create.assert_called_once_with(
        email="test@example.com",
        password_hash="hashed_password",
        display_name="John Doe"
    )

    assert result.user_id == "test-user-id"
    assert result.email_normalized == "test@example.com"
    assert result.status == "active"


@pytest.mark.asyncio
async def test_registration_with_trimmed_display_name():
    """Test that registration trims surrounding whitespace from display name."""
    # Mock dependencies
    mock_user_repo = AsyncMock(spec=IdentityUserRepository)
    mock_user_repo.get_by_email.return_value = None
    mock_hash_password = MagicMock(return_value="hashed_password")
    mock_commit = AsyncMock()
    mock_rollback = AsyncMock()

    # Create service
    service = RegistrationService(
        user_repository=mock_user_repo,
        hash_password=mock_hash_password,
        commit=mock_commit,
        rollback=mock_rollback,
    )

    # Mock the repository to return None for existing user (not found)
    mock_user_repo.get_by_email.return_value = None

    # Mock the repository create method
    mock_user = MagicMock()
    mock_user.id = "test-user-id"
    mock_user.email_normalized = "test@example.com"
    mock_user.status = "active"
    mock_user_repo.create.return_value = mock_user

    # Test registration with display name that has surrounding whitespace
    command = RegistrationCommand(
        email="test@example.com",
        password="securepassword123",
        display_name="  John Doe  "
    )

    result = await service.register(command)

    # Verify that create was called with the trimmed display name
    mock_user_repo.create.assert_called_once_with(
        email="test@example.com",
        password_hash="hashed_password",
        display_name="John Doe"
    )

    assert result.user_id == "test-user-id"


@pytest.mark.asyncio
async def test_registration_with_empty_display_name():
    """Test that registration rejects blank display names."""
    # Mock dependencies
    mock_user_repo = AsyncMock(spec=IdentityUserRepository)
    mock_user_repo.get_by_email.return_value = None
    mock_hash_password = MagicMock(return_value="hashed_password")
    mock_commit = AsyncMock()
    mock_rollback = AsyncMock()

    # Create service
    service = RegistrationService(
        user_repository=mock_user_repo,
        hash_password=mock_hash_password,
        commit=mock_commit,
        rollback=mock_rollback,
    )

    # Test registration with empty display name
    command = RegistrationCommand(
        email="test@example.com",
        password="securepassword123",
        display_name=""
    )

    with pytest.raises(RegistrationRejectedError) as exc_info:
        await service.register(command)

    assert "Display name cannot be blank" in str(exc_info.value)


@pytest.mark.asyncio
async def test_registration_with_long_display_name():
    """Test that registration rejects display names longer than 100 characters."""
    # Mock dependencies
    mock_user_repo = AsyncMock(spec=IdentityUserRepository)
    mock_user_repo.get_by_email.return_value = None
    mock_hash_password = MagicMock(return_value="hashed_password")
    mock_commit = AsyncMock()
    mock_rollback = AsyncMock()

    # Create service
    service = RegistrationService(
        user_repository=mock_user_repo,
        hash_password=mock_hash_password,
        commit=mock_commit,
        rollback=mock_rollback,
    )

    # Test registration with too long display name
    long_display_name = "a" * 101  # 101 characters

    command = RegistrationCommand(
        email="test@example.com",
        password="securepassword123",
        display_name=long_display_name
    )

    with pytest.raises(RegistrationRejectedError) as exc_info:
        await service.register(command)

    assert "Display name exceeds maximum length" in str(exc_info.value)


@pytest.mark.asyncio
async def test_registration_without_display_name():
    """Test that registration without display name remains valid."""
    # Mock dependencies
    mock_user_repo = AsyncMock(spec=IdentityUserRepository)
    mock_user_repo.get_by_email.return_value = None
    mock_hash_password = MagicMock(return_value="hashed_password")
    mock_commit = AsyncMock()
    mock_rollback = AsyncMock()

    # Create service
    service = RegistrationService(
        user_repository=mock_user_repo,
        hash_password=mock_hash_password,
        commit=mock_commit,
        rollback=mock_rollback,
    )

    # Mock the repository to return None for existing user (not found)
    mock_user_repo.get_by_email.return_value = None

    # Mock the repository create method
    mock_user = MagicMock()
    mock_user.id = "test-user-id"
    mock_user.email_normalized = "test@example.com"
    mock_user.status = "active"
    mock_user_repo.create.return_value = mock_user

    # Test registration without display name (None)
    command = RegistrationCommand(
        email="test@example.com",
        password="securepassword123",
        display_name=None
    )

    result = await service.register(command)

    # Verify that create was called with None for display name
    mock_user_repo.create.assert_called_once_with(
        email="test@example.com",
        password_hash="hashed_password",
        display_name=None
    )

    assert result.user_id == "test-user-id"


@pytest.mark.asyncio
async def test_session_introspection_includes_display_name():
    """Test that session introspection returns display_name."""
    from backend.app.stacks.identity_auth.session_introspection import get_session_introspection
    from backend.app.stacks.identity_auth.models import IdentityUser
    from unittest.mock import AsyncMock

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

    assert "display_name" in result
    assert result["display_name"] == "John Doe"
    assert "email" in result
    assert result["email"] == "test@example.com"
