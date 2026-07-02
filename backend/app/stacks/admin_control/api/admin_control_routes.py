from __future__ import annotations

from fastapi import APIRouter

from app.stacks.admin_control.services.backend_status_service import (
    get_backend_status,
)

router = APIRouter(prefix="/admin-control", tags=["admin-control"])


@router.get("/backend-status")
def backend_status() -> dict[str, object]:
    status = get_backend_status()
    return {
        "stack": status.stack,
        "phase": status.phase,
        "read_only": status.read_only,
        "backend_online": status.backend_online,
        "runtime_enabled": status.runtime_enabled,
        "broker_calls_enabled": status.broker_calls_enabled,
        "trading_enabled": status.trading_enabled,
        "mutation_enabled": status.mutation_enabled,
        "provider_calls_enabled": status.provider_calls_enabled,
        "ai_calls_enabled": status.ai_calls_enabled,
    }
