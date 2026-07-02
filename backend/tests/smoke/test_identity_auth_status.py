from app.stacks.identity_auth.services.identity_auth_service import (
    get_identity_auth_skeleton_status,
)


def test_identity_auth_status_is_skeleton_only() -> None:
    status = get_identity_auth_skeleton_status()

    assert status.stack == "identity_auth"
    assert status.phase == "phase_2_skeleton"
    assert status.login_implemented is False
    assert status.jwt_implemented is False
    assert status.password_auth_implemented is False
    assert status.business_logic_implemented is False
