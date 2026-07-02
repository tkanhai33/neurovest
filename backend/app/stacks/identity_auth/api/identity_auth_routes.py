from __future__ import annotations

from fastapi import APIRouter

from app.stacks.identity_auth.services.identity_auth_service import (
    get_identity_auth_skeleton_status,
)

router = APIRouter(prefix="/identity-auth", tags=["identity-auth"])


@router.get("/status")
def identity_auth_status() -> dict[str, object]:
    status = get_identity_auth_skeleton_status()
    return {
        "stack": status.stack,
        "phase": status.phase,
        "login_implemented": status.login_implemented,
        "jwt_implemented": status.jwt_implemented,
        "password_auth_implemented": status.password_auth_implemented,
        "business_logic_implemented": status.business_logic_implemented,
    }
