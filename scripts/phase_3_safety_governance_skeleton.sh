#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$ROOT/backend"
STACK="$BACKEND/app/stacks/safety_governance"

echo "========================================="
echo "PHASE 3 - SAFETY / GOVERNANCE SKELETON"
echo "========================================="

cd "$ROOT"

echo "Running baseline tests..."
pytest

mkdir -p "$STACK"/{contracts,domain,services,adapters,api,tests}

cat > "$STACK/contracts/safety_contract.py" <<'EOF'
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class SystemMode(StrEnum):
    OFF = "off"
    RESEARCH_ONLY = "research_only"
    PAPER = "paper"
    BROKER_READ_ONLY = "broker_read_only"
    CANARY = "canary"
    LIVE = "live"


@dataclass(frozen=True)
class SafetyGovernanceStateContract:
    stack: str = "safety_governance"
    phase: str = "phase_3_skeleton"
    system_mode: SystemMode = SystemMode.RESEARCH_ONLY
    kill_switch_enabled: bool = True
    broker_orders_enabled: bool = False
    live_trading_enabled: bool = False
    canary_trading_enabled: bool = False
    autonomous_runtime_enabled: bool = False
    ai_mutation_enabled: bool = False
    business_logic_implemented: bool = False


@dataclass(frozen=True)
class SafetyDecisionContract:
    allowed: bool
    reason: str
EOF

cat > "$STACK/services/safety_governance_service.py" <<'EOF'
from __future__ import annotations

from app.stacks.safety_governance.contracts.safety_contract import (
    SafetyDecisionContract,
    SafetyGovernanceStateContract,
)


def get_safety_governance_state() -> SafetyGovernanceStateContract:
    return SafetyGovernanceStateContract()


def deny_all_execution_in_skeleton() -> SafetyDecisionContract:
    return SafetyDecisionContract(
        allowed=False,
        reason="Phase 3 skeleton denies all execution paths.",
    )
EOF

cat > "$STACK/api/safety_governance_routes.py" <<'EOF'
from __future__ import annotations

from fastapi import APIRouter

from app.stacks.safety_governance.services.safety_governance_service import (
    deny_all_execution_in_skeleton,
    get_safety_governance_state,
)

router = APIRouter(prefix="/safety-governance", tags=["safety-governance"])


@router.get("/status")
def safety_governance_status() -> dict[str, object]:
    state = get_safety_governance_state()
    return {
        "stack": state.stack,
        "phase": state.phase,
        "system_mode": state.system_mode,
        "kill_switch_enabled": state.kill_switch_enabled,
        "broker_orders_enabled": state.broker_orders_enabled,
        "live_trading_enabled": state.live_trading_enabled,
        "canary_trading_enabled": state.canary_trading_enabled,
        "autonomous_runtime_enabled": state.autonomous_runtime_enabled,
        "ai_mutation_enabled": state.ai_mutation_enabled,
        "business_logic_implemented": state.business_logic_implemented,
    }


@router.get("/execution-decision")
def execution_decision() -> dict[str, object]:
    decision = deny_all_execution_in_skeleton()
    return {
        "allowed": decision.allowed,
        "reason": decision.reason,
    }
EOF

cat > "$STACK/domain/README.md" <<'EOF'
# Safety/Governance Domain

Phase 3 skeleton only.

Allowed:
- safety state contracts
- system mode enum
- execution-denial skeleton contract
- testable status

Forbidden:
- real mode mutation
- real permission logic
- broker unlock logic
- live trading unlock logic
- runtime enablement logic
- AI mutation unlock logic
EOF

cat > "$STACK/adapters/README.md" <<'EOF'
# Safety/Governance Adapters

Phase 3 skeleton only.

No external policy providers.
No broker provider adapters.
No runtime adapters.
EOF

cat > "$STACK/tests/README.md" <<'EOF'
# Safety/Governance Stack Tests

Phase 3 uses root backend tests for certification.
EOF

cat > "$STACK/README.md" <<'EOF'
# safety_governance

Phase 3 — Safety / Governance Skeleton.

Owns:
- system mode contract
- kill switch state
- broker/live/canary locks
- autonomous runtime lock
- AI mutation lock
- execution denial skeleton

Forbidden in Phase 3:
- broker unlock implementation
- live trading implementation
- real mode mutation
- permission enforcement implementation
- runtime scheduling
- business logic
EOF

cat > "$BACKEND/tests/contracts/test_safety_governance_contract.py" <<'EOF'
from app.stacks.safety_governance.contracts.safety_contract import (
    SafetyDecisionContract,
    SafetyGovernanceStateContract,
    SystemMode,
)


def test_safety_governance_default_state_locked() -> None:
    state = SafetyGovernanceStateContract()

    assert state.stack == "safety_governance"
    assert state.phase == "phase_3_skeleton"
    assert state.system_mode == SystemMode.RESEARCH_ONLY
    assert state.kill_switch_enabled is True
    assert state.broker_orders_enabled is False
    assert state.live_trading_enabled is False
    assert state.canary_trading_enabled is False
    assert state.autonomous_runtime_enabled is False
    assert state.ai_mutation_enabled is False
    assert state.business_logic_implemented is False


def test_safety_decision_contract_shape() -> None:
    decision = SafetyDecisionContract(allowed=False, reason="locked")

    assert decision.allowed is False
    assert decision.reason == "locked"
EOF

cat > "$BACKEND/tests/smoke/test_safety_governance_status.py" <<'EOF'
from app.stacks.safety_governance.services.safety_governance_service import (
    deny_all_execution_in_skeleton,
    get_safety_governance_state,
)


def test_safety_governance_status_is_locked() -> None:
    state = get_safety_governance_state()

    assert state.kill_switch_enabled is True
    assert state.broker_orders_enabled is False
    assert state.live_trading_enabled is False
    assert state.canary_trading_enabled is False
    assert state.autonomous_runtime_enabled is False
    assert state.ai_mutation_enabled is False


def test_safety_governance_denies_execution() -> None:
    decision = deny_all_execution_in_skeleton()

    assert decision.allowed is False
    assert "denies all execution" in decision.reason
EOF

cat > "$BACKEND/tests/architecture/test_safety_governance_phase_3_forbidden_terms.py" <<'EOF'
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STACK = ROOT / "app" / "stacks" / "safety_governance"

FORBIDDEN_TERMS = [
    "enable_live_trading",
    "unlock_broker_orders",
    "set_live_mode",
    "place_order",
    "submit_order",
    "execute_trade",
    "enable_autonomous_runtime",
    "enable_ai_mutation",
]


def test_safety_governance_phase_3_has_no_unlock_implementation() -> None:
    scanned = []

    for path in STACK.rglob("*.py"):
        text = path.read_text(errors="ignore")
        scanned.append(path)

        for term in FORBIDDEN_TERMS:
            assert term not in text, f"Forbidden safety implementation term {term!r} found in {path}"

    assert scanned
EOF

cat > "$ROOT/docs/contracts/PHASE_3_SAFETY_GOVERNANCE_SKELETON_CONTRACT.md" <<'EOF'
# Phase 3 Safety / Governance Skeleton Contract

## Status

Phase 3 skeleton only.

## Purpose

Create the safety/governance stack shape without implementing real mode changes or unlock behavior.

## Allowed

- system mode enum
- safety state contract
- execution-denial skeleton
- status service
- API placeholder
- tests
- certification artifact

## Forbidden

- broker unlock implementation
- live trading unlock implementation
- canary unlock implementation
- runtime unlock implementation
- AI mutation unlock implementation
- real permission enforcement
- business logic

## Default State

- system mode: research_only
- kill switch: enabled
- broker orders: disabled
- live trading: disabled
- canary trading: disabled
- autonomous runtime: disabled
- AI mutation: disabled

## Exit Criteria

- tests pass
- safety_governance stack has contracts/services/api placeholders
- all execution paths denied
- no real unlock implementation exists
EOF

cat > "$ROOT/certification/phase_01/PHASE_3_SAFETY_GOVERNANCE_SKELETON_CERTIFICATION.md" <<'EOF'
# Phase 3 Safety / Governance Skeleton Certification

Status: pending

Checks:
- safety_governance contract exists
- skeleton service exists
- API placeholder exists
- execution denied by default
- no broker unlock implementation
- no live trading unlock implementation
- no AI mutation unlock implementation
- tests pass
EOF

echo
echo "Running Phase 3 tests..."
pytest

cat > "$ROOT/certification/phase_01/PHASE_3_SAFETY_GOVERNANCE_SKELETON_CERTIFICATION.md" <<'EOF'
# Phase 3 Safety / Governance Skeleton Certification

Status: PASS

Checks:
- safety_governance contract exists
- skeleton service exists
- API placeholder exists
- execution denied by default
- no broker unlock implementation
- no live trading unlock implementation
- no AI mutation unlock implementation
- tests pass

Result:
- Phase 3 safety/governance skeleton is certified.
EOF

echo
echo "========================================="
echo "PHASE 3 COMPLETE"
echo "========================================="
echo "PASS: Safety/Governance skeleton created and certified."
