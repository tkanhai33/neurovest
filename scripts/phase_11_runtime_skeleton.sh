#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$ROOT/backend"
STACK="$BACKEND/app/stacks/runtime"

echo "========================================="
echo "PHASE 11 - RUNTIME SKELETON"
echo "========================================="

cd "$ROOT"

echo "Running baseline tests..."
pytest

mkdir -p "$STACK"/{contracts,domain,services,adapters,api,tests}

cat > "$STACK/contracts/runtime_contract.py" <<'EOF'
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class RuntimeWorkflowStatus(StrEnum):
    DISABLED = "disabled"
    SKELETON_ONLY = "skeleton_only"
    READY_FOR_REVIEW = "ready_for_review"


class RuntimeJobType(StrEnum):
    MANUAL_RESEARCH_REFRESH = "manual_research_refresh"
    MANUAL_PORTFOLIO_REFRESH = "manual_portfolio_refresh"
    MANUAL_PAPER_REVIEW = "manual_paper_review"


@dataclass(frozen=True)
class RuntimeWorkflowContract:
    workflow_id: str
    job_type: RuntimeJobType
    status: RuntimeWorkflowStatus = RuntimeWorkflowStatus.DISABLED


@dataclass(frozen=True)
class RuntimeScheduleContract:
    schedule_id: str
    workflow_id: str
    enabled: bool = False


@dataclass(frozen=True)
class RuntimeEventContract:
    event_id: str
    workflow_id: str
    event_name: str


@dataclass(frozen=True)
class RuntimeSkeletonStatus:
    stack: str = "runtime"
    phase: str = "phase_11_skeleton"
    scheduler_implemented: bool = False
    background_loops_enabled: bool = False
    workflow_execution_implemented: bool = False
    strategy_execution_implemented: bool = False
    paper_trading_integration_implemented: bool = False
    broker_integration_implemented: bool = False
    mutation_logic_implemented: bool = False
    business_logic_implemented: bool = False
EOF

cat > "$STACK/services/runtime_service.py" <<'EOF'
from __future__ import annotations

from app.stacks.runtime.contracts.runtime_contract import (
    RuntimeSkeletonStatus,
    RuntimeWorkflowContract,
    RuntimeWorkflowStatus,
)


def get_runtime_skeleton_status() -> RuntimeSkeletonStatus:
    return RuntimeSkeletonStatus()


def disable_runtime_workflow_in_skeleton(
    workflow: RuntimeWorkflowContract,
) -> RuntimeWorkflowContract:
    return RuntimeWorkflowContract(
        workflow_id=workflow.workflow_id,
        job_type=workflow.job_type,
        status=RuntimeWorkflowStatus.DISABLED,
    )
EOF

cat > "$STACK/api/runtime_routes.py" <<'EOF'
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
EOF

cat > "$STACK/domain/README.md" <<'EOF'
# Runtime Domain

Phase 11 skeleton only.

Allowed:
- runtime workflow contracts
- runtime job type contracts
- runtime schedule contracts
- runtime event contracts
- disabled runtime status

Forbidden:
- background loops
- scheduler implementation
- autonomous execution
- strategy execution
- paper trading execution
- broker execution
- mutation logic
EOF

cat > "$STACK/adapters/README.md" <<'EOF'
# Runtime Adapters

Phase 11 skeleton only.

No scheduler adapters.
No broker adapters.
No execution adapters.
No background workers.
EOF

cat > "$STACK/tests/README.md" <<'EOF'
# Runtime Stack Tests

Phase 11 uses root backend tests for certification.
EOF

cat > "$STACK/README.md" <<'EOF'
# runtime

Phase 11 — Runtime Skeleton.

Owns:
- workflow contracts
- schedule contracts
- runtime event contracts
- future orchestration boundary

Forbidden in Phase 11:
- background loops
- scheduler implementation
- autonomous execution
- broker calls
- strategy execution
- paper trading execution
- mutation logic
EOF

cat > "$BACKEND/tests/contracts/test_runtime_contract.py" <<'EOF'
from app.stacks.runtime.contracts.runtime_contract import (
    RuntimeEventContract,
    RuntimeJobType,
    RuntimeScheduleContract,
    RuntimeSkeletonStatus,
    RuntimeWorkflowContract,
    RuntimeWorkflowStatus,
)


def test_runtime_workflow_contract_shape() -> None:
    workflow = RuntimeWorkflowContract(
        workflow_id="workflow_001",
        job_type=RuntimeJobType.MANUAL_RESEARCH_REFRESH,
    )

    assert workflow.workflow_id == "workflow_001"
    assert workflow.job_type == RuntimeJobType.MANUAL_RESEARCH_REFRESH
    assert workflow.status == RuntimeWorkflowStatus.DISABLED


def test_runtime_schedule_contract_shape() -> None:
    schedule = RuntimeScheduleContract(
        schedule_id="schedule_001",
        workflow_id="workflow_001",
    )

    assert schedule.schedule_id == "schedule_001"
    assert schedule.workflow_id == "workflow_001"
    assert schedule.enabled is False


def test_runtime_event_contract_shape() -> None:
    event = RuntimeEventContract(
        event_id="event_001",
        workflow_id="workflow_001",
        event_name="placeholder_event",
    )

    assert event.event_id == "event_001"
    assert event.workflow_id == "workflow_001"
    assert event.event_name == "placeholder_event"


def test_runtime_skeleton_status_locked() -> None:
    status = RuntimeSkeletonStatus()

    assert status.stack == "runtime"
    assert status.phase == "phase_11_skeleton"
    assert status.scheduler_implemented is False
    assert status.background_loops_enabled is False
    assert status.workflow_execution_implemented is False
    assert status.strategy_execution_implemented is False
    assert status.paper_trading_integration_implemented is False
    assert status.broker_integration_implemented is False
    assert status.mutation_logic_implemented is False
    assert status.business_logic_implemented is False
EOF

cat > "$BACKEND/tests/smoke/test_runtime_status.py" <<'EOF'
from app.stacks.runtime.contracts.runtime_contract import (
    RuntimeJobType,
    RuntimeWorkflowContract,
    RuntimeWorkflowStatus,
)
from app.stacks.runtime.services.runtime_service import (
    disable_runtime_workflow_in_skeleton,
    get_runtime_skeleton_status,
)


def test_runtime_status_is_skeleton_only() -> None:
    status = get_runtime_skeleton_status()

    assert status.stack == "runtime"
    assert status.phase == "phase_11_skeleton"
    assert status.scheduler_implemented is False
    assert status.background_loops_enabled is False
    assert status.workflow_execution_implemented is False
    assert status.strategy_execution_implemented is False
    assert status.paper_trading_integration_implemented is False
    assert status.broker_integration_implemented is False
    assert status.mutation_logic_implemented is False
    assert status.business_logic_implemented is False


def test_runtime_skeleton_disables_workflows() -> None:
    workflow = RuntimeWorkflowContract(
        workflow_id="workflow_001",
        job_type=RuntimeJobType.MANUAL_RESEARCH_REFRESH,
        status=RuntimeWorkflowStatus.SKELETON_ONLY,
    )

    disabled = disable_runtime_workflow_in_skeleton(workflow)

    assert disabled.workflow_id == "workflow_001"
    assert disabled.status == RuntimeWorkflowStatus.DISABLED
EOF

cat > "$BACKEND/tests/architecture/test_runtime_phase_11_forbidden_terms.py" <<'EOF'
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STACK = ROOT / "app" / "stacks" / "runtime"

FORBIDDEN_TERMS = [
    "while True",
    "asyncio.create_task",
    "BackgroundTasks",
    "APScheduler",
    "schedule.every",
    "run_scheduler",
    "execute_workflow",
    "execute_trade",
    "submit_order",
    "place_order",
    "broker_client",
    "mutate_strategy",
]


def test_runtime_phase_11_has_no_scheduler_or_execution_logic() -> None:
    scanned = []

    for path in STACK.rglob("*.py"):
        text = path.read_text(errors="ignore")
        scanned.append(path)

        for term in FORBIDDEN_TERMS:
            assert term not in text, f"Forbidden runtime implementation term {term!r} found in {path}"

    assert scanned
EOF

cat > "$ROOT/docs/contracts/PHASE_11_RUNTIME_SKELETON_CONTRACT.md" <<'EOF'
# Phase 11 Runtime Skeleton Contract

## Status

Phase 11 skeleton only.

## Purpose

Create the runtime orchestration stack shape without implementing schedulers, background loops, workflow execution, strategy execution, paper trading execution, broker interaction, mutation logic, or business logic.

## Allowed

- runtime workflow contract
- runtime job type contract
- runtime schedule contract
- runtime event contract
- disabled workflow service
- status service
- API placeholder
- tests
- certification artifact

## Forbidden

- scheduler implementation
- background loops
- autonomous execution
- workflow execution
- strategy execution
- paper trading execution
- broker interaction
- mutation logic
- business logic

## Default State

- scheduler implemented: false
- background loops enabled: false
- workflow execution implemented: false
- strategy execution implemented: false
- paper trading integration implemented: false
- broker integration implemented: false
- mutation logic implemented: false

## Exit Criteria

- tests pass
- runtime stack has contracts/services/api placeholders
- all workflows disabled by skeleton
- no scheduler exists
- no background loop exists
- no execution logic exists
EOF

cat > "$ROOT/certification/phase_01/PHASE_11_RUNTIME_SKELETON_CERTIFICATION.md" <<'EOF'
# Phase 11 Runtime Skeleton Certification

Status: pending

Checks:
- runtime contract exists
- skeleton service exists
- API placeholder exists
- all workflows disabled by default
- no scheduler implementation
- no background loops
- no execution implementation
- no broker implementation
- tests pass
EOF

echo
echo "Running Phase 11 tests..."
pytest

cat > "$ROOT/certification/phase_01/PHASE_11_RUNTIME_SKELETON_CERTIFICATION.md" <<'EOF'
# Phase 11 Runtime Skeleton Certification

Status: PASS

Checks:
- runtime contract exists
- skeleton service exists
- API placeholder exists
- all workflows disabled by default
- no scheduler implementation
- no background loops
- no execution implementation
- no broker implementation
- tests pass

Result:
- Phase 11 runtime skeleton is certified.
EOF

echo
echo "========================================="
echo "PHASE 11 COMPLETE"
echo "========================================="
echo "PASS: Runtime skeleton created and certified."
