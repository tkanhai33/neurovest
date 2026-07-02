from __future__ import annotations

from app.stacks.admin_control.contracts.backend_status_contract import (
    BackendStatusContract,
)


def get_backend_status() -> BackendStatusContract:
    return BackendStatusContract()
