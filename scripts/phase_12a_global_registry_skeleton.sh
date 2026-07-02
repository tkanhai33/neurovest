#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$ROOT/backend"
REGISTRY="$BACKEND/app/shared/contracts"

echo "========================================="
echo "PHASE 12A - GLOBAL REGISTRY SKELETON"
echo "========================================="

cd "$ROOT"

echo "Running baseline tests..."
pytest

mkdir -p "$REGISTRY"

cat > "$REGISTRY/stack_registry.py" <<'EOF'
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class StackName(StrEnum):
    IDENTITY_AUTH = "identity_auth"
    SAFETY_GOVERNANCE = "safety_governance"
    MARKET_DATA = "market_data"
    PORTFOLIO = "portfolio"
    RESEARCH = "research"
    STRATEGY = "strategy"
    RISK = "risk"
    PAPER_TRADING = "paper_trading"
    BROKER_INTEGRATION = "broker_integration"
    RUNTIME = "runtime"
    AI_CHAT = "ai_chat"
    ADMIN_CONTROL = "admin_control"


@dataclass(frozen=True)
class StackRegistryEntry:
    name: StackName
    phase: str
    implemented: bool = False
    business_logic_enabled: bool = False


STACK_REGISTRY: tuple[StackRegistryEntry, ...] = (
    StackRegistryEntry(StackName.IDENTITY_AUTH, "phase_2_skeleton"),
    StackRegistryEntry(StackName.SAFETY_GOVERNANCE, "phase_3_skeleton"),
    StackRegistryEntry(StackName.MARKET_DATA, "phase_4_skeleton"),
    StackRegistryEntry(StackName.PORTFOLIO, "phase_5_skeleton"),
    StackRegistryEntry(StackName.RESEARCH, "phase_6_skeleton"),
    StackRegistryEntry(StackName.STRATEGY, "phase_7_skeleton"),
    StackRegistryEntry(StackName.RISK, "phase_8_skeleton"),
    StackRegistryEntry(StackName.PAPER_TRADING, "phase_9_skeleton"),
    StackRegistryEntry(StackName.BROKER_INTEGRATION, "phase_10_skeleton"),
    StackRegistryEntry(StackName.RUNTIME, "phase_11_skeleton"),
    StackRegistryEntry(StackName.AI_CHAT, "phase_12_skeleton"),
    StackRegistryEntry(StackName.ADMIN_CONTROL, "phase_0_skeleton"),
)
EOF

cat > "$REGISTRY/phase_registry.py" <<'EOF'
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PhaseRegistryEntry:
    phase: str
    name: str
    status: str


PHASE_REGISTRY: tuple[PhaseRegistryEntry, ...] = (
    PhaseRegistryEntry("phase_1", "foundation", "certified"),
    PhaseRegistryEntry("phase_2", "identity_auth_skeleton", "certified"),
    PhaseRegistryEntry("phase_3", "safety_governance_skeleton", "certified"),
    PhaseRegistryEntry("phase_4", "market_data_skeleton", "certified"),
    PhaseRegistryEntry("phase_5", "portfolio_skeleton", "certified"),
    PhaseRegistryEntry("phase_6", "research_skeleton", "certified"),
    PhaseRegistryEntry("phase_7", "strategy_skeleton", "certified"),
    PhaseRegistryEntry("phase_8", "risk_skeleton", "certified"),
    PhaseRegistryEntry("phase_9", "paper_trading_skeleton", "certified"),
    PhaseRegistryEntry("phase_10", "broker_integration_skeleton", "certified"),
    PhaseRegistryEntry("phase_11", "runtime_skeleton", "certified"),
    PhaseRegistryEntry("phase_12", "ai_chat_skeleton", "certified"),
    PhaseRegistryEntry("phase_12a", "global_registry_skeleton", "skeleton"),
)
EOF

cat > "$REGISTRY/feature_registry.py" <<'EOF'
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FeatureFlag:
    name: str
    enabled: bool = False
    reason: str = "disabled_by_default"


FEATURE_FLAGS: tuple[FeatureFlag, ...] = (
    FeatureFlag("live_trading"),
    FeatureFlag("canary_trading"),
    FeatureFlag("broker_orders"),
    FeatureFlag("broker_read_only_calls"),
    FeatureFlag("market_data_provider_calls"),
    FeatureFlag("strategy_scoring"),
    FeatureFlag("risk_approval_engine"),
    FeatureFlag("paper_trading_fill_engine"),
    FeatureFlag("runtime_scheduler"),
    FeatureFlag("ai_model_calls"),
    FeatureFlag("ai_tool_use"),
    FeatureFlag("ai_memory"),
    FeatureFlag("ai_rag"),
)
EOF

cat > "$REGISTRY/system_state.py" <<'EOF'
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SystemState:
    project: str = "NeuroVest"
    phase: str = "phase_12a_global_registry_skeleton"
    foundation_certified: bool = True
    skeletons_certified: bool = True
    business_logic_enabled: bool = False
    live_trading_enabled: bool = False
    broker_orders_enabled: bool = False
    autonomous_runtime_enabled: bool = False
    ai_mutation_enabled: bool = False


def get_system_state() -> SystemState:
    return SystemState()
EOF

cat > "$REGISTRY/README.md" <<'EOF'
# Shared Contract Registries

Phase 12A skeleton only.

Owns:
- stack registry
- phase registry
- feature registry
- system state contract

Forbidden:
- runtime mutation
- feature enabling
- broker unlocking
- live trading unlocking
- business logic
EOF

cat > "$BACKEND/tests/contracts/test_global_registry_contracts.py" <<'EOF'
from app.shared.contracts.feature_registry import FEATURE_FLAGS
from app.shared.contracts.phase_registry import PHASE_REGISTRY
from app.shared.contracts.stack_registry import STACK_REGISTRY, StackName
from app.shared.contracts.system_state import get_system_state


def test_stack_registry_contains_core_stacks() -> None:
    names = {entry.name for entry in STACK_REGISTRY}

    assert StackName.IDENTITY_AUTH in names
    assert StackName.SAFETY_GOVERNANCE in names
    assert StackName.MARKET_DATA in names
    assert StackName.PORTFOLIO in names
    assert StackName.RESEARCH in names
    assert StackName.STRATEGY in names
    assert StackName.RISK in names
    assert StackName.PAPER_TRADING in names
    assert StackName.BROKER_INTEGRATION in names
    assert StackName.RUNTIME in names
    assert StackName.AI_CHAT in names


def test_stack_registry_business_logic_disabled() -> None:
    assert all(entry.business_logic_enabled is False for entry in STACK_REGISTRY)


def test_phase_registry_contains_phase_12a() -> None:
    phases = {entry.phase for entry in PHASE_REGISTRY}

    assert "phase_12a" in phases


def test_feature_flags_disabled_by_default() -> None:
    assert FEATURE_FLAGS
    assert all(flag.enabled is False for flag in FEATURE_FLAGS)


def test_system_state_locked() -> None:
    state = get_system_state()

    assert state.project == "NeuroVest"
    assert state.foundation_certified is True
    assert state.skeletons_certified is True
    assert state.business_logic_enabled is False
    assert state.live_trading_enabled is False
    assert state.broker_orders_enabled is False
    assert state.autonomous_runtime_enabled is False
    assert state.ai_mutation_enabled is False
EOF

cat > "$BACKEND/tests/architecture/test_global_registry_phase_12a_forbidden_terms.py" <<'EOF'
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "app" / "shared" / "contracts"

FORBIDDEN_TERMS = [
    "enable_live_trading",
    "enable_broker_orders",
    "enable_runtime_scheduler",
    "enable_ai_mutation",
    "submit_order",
    "place_order",
    "execute_trade",
    "runtime_loop",
    "mutate_strategy",
]


def test_global_registry_has_no_unlock_or_runtime_logic() -> None:
    scanned = []

    for path in REGISTRY.rglob("*.py"):
        text = path.read_text(errors="ignore")
        scanned.append(path)

        for term in FORBIDDEN_TERMS:
            assert term not in text, f"Forbidden registry implementation term {term!r} found in {path}"

    assert scanned
EOF

cat > "$ROOT/docs/contracts/PHASE_12A_GLOBAL_REGISTRY_SKELETON_CONTRACT.md" <<'EOF'
# Phase 12A Global Registry Skeleton Contract

## Status

Phase 12A skeleton only.

## Purpose

Create shared registry contracts for stack ownership, phase state, feature flags, and locked system state before frontend skeleton work begins.

## Allowed

- stack registry
- phase registry
- feature registry
- system state contract
- tests
- certification artifact

## Forbidden

- runtime mutation
- feature enabling
- broker unlocking
- live trading unlocking
- scheduler enabling
- AI mutation enabling
- business logic

## Default State

- business logic: disabled
- live trading: disabled
- broker orders: disabled
- autonomous runtime: disabled
- AI mutation: disabled
- feature flags: disabled by default

## Exit Criteria

- tests pass
- registry files exist
- feature flags are disabled
- system state is locked
- no unlock/runtime logic exists
EOF

cat > "$ROOT/certification/phase_01/PHASE_12A_GLOBAL_REGISTRY_SKELETON_CERTIFICATION.md" <<'EOF'
# Phase 12A Global Registry Skeleton Certification

Status: pending

Checks:
- stack registry exists
- phase registry exists
- feature registry exists
- system state exists
- all feature flags disabled
- no runtime unlock logic
- no broker unlock logic
- tests pass
EOF

echo
echo "Running Phase 12A tests..."
pytest

cat > "$ROOT/certification/phase_01/PHASE_12A_GLOBAL_REGISTRY_SKELETON_CERTIFICATION.md" <<'EOF'
# Phase 12A Global Registry Skeleton Certification

Status: PASS

Checks:
- stack registry exists
- phase registry exists
- feature registry exists
- system state exists
- all feature flags disabled
- no runtime unlock logic
- no broker unlock logic
- tests pass

Result:
- Phase 12A global registry skeleton is certified.
EOF

echo
echo "========================================="
echo "PHASE 12A COMPLETE"
echo "========================================="
echo "PASS: Global registry skeleton created and certified."
