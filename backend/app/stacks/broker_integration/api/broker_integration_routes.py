from __future__ import annotations

from fastapi import APIRouter

from app.stacks.broker_integration.services.broker_integration_service import (
    get_broker_integration_skeleton_status,
)

router = APIRouter(prefix="/broker-integration", tags=["broker-integration"])


@router.get("/status")
def broker_integration_status() -> dict[str, object]:
    status = get_broker_integration_skeleton_status()
    return {
        "stack": status.stack,
        "phase": status.phase,
        "provider": status.provider,
        "broker_auth_implemented": status.broker_auth_implemented,
        "token_storage_implemented": status.token_storage_implemented,
        "account_sync_implemented": status.account_sync_implemented,
        "read_only_calls_enabled": status.read_only_calls_enabled,
        "order_preview_implemented": status.order_preview_implemented,
        "order_submission_implemented": status.order_submission_implemented,
        "live_trading_implemented": status.live_trading_implemented,
        "business_logic_implemented": status.business_logic_implemented,
    }
