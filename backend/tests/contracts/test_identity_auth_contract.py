from app.stacks.identity_auth.contracts.identity_contract import (
    AccountStatus,
    IdentityAuthSkeletonStatus,
    IdentityUserContract,
    UserRole,
)


def test_identity_user_contract_shape() -> None:
    user = IdentityUserContract(
        id="user_001",
        email="test@example.com",
        role=UserRole.USER,
        status=AccountStatus.ACTIVE,
    )

    assert user.id == "user_001"
    assert user.email == "test@example.com"
    assert user.role == UserRole.USER
    assert user.status == AccountStatus.ACTIVE


def test_identity_auth_skeleton_has_no_real_auth() -> None:
    status = IdentityAuthSkeletonStatus()

    assert status.stack == "identity_auth"
    assert status.phase == "phase_2_skeleton"
    assert status.login_implemented is False
    assert status.jwt_implemented is False
    assert status.password_auth_implemented is False
    assert status.business_logic_implemented is False
