from __future__ import annotations

from fastapi import APIRouter

from app.stacks.runtime.services.runtime_service import (
    get_runtime_skeleton_status,
)

router = APIRouter(prefix="/runtime", tags=["runtime"])


@router.get("/status")
def runtime_status() -> dict[str, object]:
    status = get_runtime_skeleton_status()
    return {
        "stack": status.stack,
        "phase": status.phase,
        "scheduler_implemented": status.scheduler_implemented,
        "background_loops_enabled": status.background_loops_enabled,
        "workflow_execution_implemented": status.workflow_execution_implemented,
        "strategy_execution_implemented": status.strategy_execution_implemented,
        "paper_trading_integration_implemented": status.paper_trading_integration_implemented,
        "broker_integration_implemented": status.broker_integration_implemented,
        "mutation_logic_implemented": status.mutation_logic_implemented,
        "business_logic_implemented": status.business_logic_implemented,
    }
