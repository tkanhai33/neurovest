import pytest
from unittest.mock import AsyncMock, MagicMock

from backend.app.stacks.identity_auth.registration_service import (
    RegistrationService,
)
from backend.app.stacks.identity_auth.repositories import IdentityUserRepository
from backend.app.stacks.identity_auth.service_contracts import (
    RegistrationCommand,
    RegistrationRejectedError,
)


@pytest.mark.asyncio
async def test_successful_registration():
    """Test successful registration."""
    # Mock dependencies
    mock_user_repo = AsyncMock(spec=IdentityUserRepository)
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

    # Test registration
    command = RegistrationCommand(
        email="test@example.com",
        password="securepassword123",
    )

    result = await service.register(command)

    assert result.user_id == "test-user-id"
    assert result.email_normalized == "test@example.com"
    assert result.status == "active"


@pytest.mark.asyncio
async def test_registration_with_existing_email():
    """Test registration fails when email already exists."""
    # Mock dependencies
    mock_user_repo = AsyncMock(spec=IdentityUserRepository)
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

    # Mock the repository to return an existing user
    mock_existing_user = MagicMock()
    mock_user_repo.get_by_email.return_value = mock_existing_user

    # Test registration with existing email
    command = RegistrationCommand(
        email="test@example.com",
        password="securepassword123",
    )

    with pytest.raises(RegistrationRejectedError):
        await service.register(command)

    # Verify rollback was called
    mock_rollback.assert_called_once()


@pytest.mark.asyncio
async def test_registration_with_invalid_password():
    """Test registration fails when password is invalid."""
    # Mock dependencies
    mock_user_repo = AsyncMock(spec=IdentityUserRepository)
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

    # Test registration with invalid password
    command = RegistrationCommand(
        email="test@example.com",
        password="",  # Empty password
    )

    with pytest.raises(RegistrationRejectedError):
        await service.register(command)

    # Verify rollback was called
    mock_rollback.assert_called_once()
