from __future__ import annotations

from app.stacks.identity_auth.contracts.identity_contract import (
    IdentityAuthSkeletonStatus,
)


def get_identity_auth_skeleton_status() -> IdentityAuthSkeletonStatus:
    return IdentityAuthSkeletonStatus()
