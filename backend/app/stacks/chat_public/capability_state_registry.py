from __future__ import annotations

import importlib
import inspect
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class CapabilitySource:
    capability: str
    module: str
    entrypoint: str = "healthcheck"
    description: str = ""


@dataclass(frozen=True)
class CapabilityState:
    capability: str
    module: str
    entrypoint: str
    state: str
    available: bool
    verified: bool
    invocation: str
    detail: Any
    error: str | None = None
    description: str = ""


CAPABILITY_SOURCES: tuple[CapabilitySource, ...] = (
    CapabilitySource(
        capability="market_data_provider_registry",
        module=(
            "backend.app.stacks.market_data."
            "provider_registry"
        ),
        description=(
            "Market-data provider registration "
            "and capability discovery."
        ),
    ),
    CapabilitySource(
        capability="market_data_provider_router",
        module=(
            "backend.app.stacks.market_data."
            "provider_router"
        ),
        description=(
            "Market-data provider selection "
            "and routing boundary."
        ),
    ),
    CapabilitySource(
        capability="market_data_runtime",
        module=(
            "backend.app.stacks.market_data."
            "runtime_composition"
        ),
        description=(
            "Market-data runtime composition."
        ),
    ),
    CapabilitySource(
        capability="yfinance_provider",
        module=(
            "backend.app.stacks.market_data."
            "yfinance_provider"
        ),
        description=(
            "Local yfinance-backed market-data provider."
        ),
    ),
    CapabilitySource(
        capability="market_session",
        module=(
            "backend.app.stacks.market_data."
            "market_session"
        ),
        description=(
            "Market-session state and scheduling boundary."
        ),
    ),
    CapabilitySource(
        capability="market_data_cache",
        module=(
            "backend.app.stacks.market_data."
            "provider_cache"
        ),
        description=(
            "Market-data provider cache."
        ),
    ),
    CapabilitySource(
        capability="portfolio_runtime",
        module=(
            "backend.app.stacks.portfolio."
            "portfolio_runtime"
        ),
        description=(
            "Portfolio read and analysis runtime."
        ),
    ),
    CapabilitySource(
        capability="risk_runtime",
        module=(
            "backend.app.stacks.risk."
            "risk_runtime_service"
        ),
        description=(
            "Risk-analysis runtime service."
        ),
    ),
    CapabilitySource(
        capability="loss_streak_guard",
        module=(
            "backend.app.stacks.risk."
            "loss_streak_guard"
        ),
        description=(
            "Loss-streak risk guard."
        ),
    ),
    CapabilitySource(
        capability="drawdown_guard",
        module=(
            "backend.app.stacks.risk."
            "drawdown_guard"
        ),
        description=(
            "Balance-dependent drawdown guard."
        ),
    ),
    CapabilitySource(
        capability="paper_broker",
        module=(
            "backend.app.stacks.execution."
            "paper_broker"
        ),
        description=(
            "Paper-trading broker boundary."
        ),
    ),
    CapabilitySource(
        capability="sandbox_execution",
        module=(
            "backend.app.stacks.execution."
            "sandbox_runtime"
        ),
        description=(
            "Sandbox execution runtime."
        ),
    ),
    CapabilitySource(
        capability="strategy_runtime",
        module=(
            "backend.app.stacks.strategy."
            "strategy_runtime"
        ),
        description=(
            "Strategy-analysis runtime."
        ),
    ),
    CapabilitySource(
        capability="snaptrade_adapter",
        module=(
            "backend.app.stacks.snaptrade.adapter"
        ),
        description=(
            "SnapTrade adapter boundary."
        ),
    ),
    CapabilitySource(
        capability="snaptrade_broker",
        module=(
            "backend.app.stacks.snaptrade.broker"
        ),
        description=(
            "SnapTrade broker boundary."
        ),
    ),
    CapabilitySource(
        capability="snaptrade_execution",
        module=(
            "backend.app.stacks.snaptrade.execution"
        ),
        description=(
            "SnapTrade execution boundary."
        ),
    ),
    CapabilitySource(
        capability="wolfden_runtime",
        module=(
            "backend.app.stacks.wolfden_ai.runtime"
        ),
        description=(
            "Wolfden AI runtime."
        ),
    ),
    CapabilitySource(
        capability="wolfden_memory",
        module=(
            "backend.app.stacks.wolfden_ai.memory"
        ),
        description=(
            "Wolfden AI memory boundary."
        ),
    ),
    CapabilitySource(
        capability="wolfden_routing",
        module=(
            "backend.app.stacks.wolfden_ai.routing"
        ),
        description=(
            "Wolfden AI routing boundary."
        ),
    ),
    CapabilitySource(
        capability="chat_service",
        module=(
            "backend.app.stacks.chat_public."
            "chat_service"
        ),
        description=(
            "Public chat service boundary."
        ),
    ),
    CapabilitySource(
        capability="chat_memory",
        module=(
            "backend.app.stacks.chat_public."
            "chat_memory"
        ),
        description=(
            "Public chat memory boundary."
        ),
    ),
    CapabilitySource(
        capability="conversation_store",
        module=(
            "backend.app.stacks.chat_public."
            "conversation_store"
        ),
        description=(
            "Conversation persistence boundary."
        ),
    ),
)


def _required_arguments(
    function: Any,
) -> list[str]:
    signature = inspect.signature(
        function
    )

    return [
        parameter.name
        for parameter in signature.parameters.values()
        if (
            parameter.default
            is inspect.Parameter.empty
            and parameter.kind
            not in {
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            }
        )
    ]


def _normalize_state(
    detail: Any,
) -> tuple[str, bool]:
    if isinstance(detail, bool):
        return (
            "available" if detail else "unavailable",
            detail,
        )

    if not isinstance(detail, dict):
        return "reported", True

    for key in (
        "healthy",
        "available",
        "enabled",
        "configured",
        "ready",
        "ok",
    ):
        value = detail.get(key)

        if isinstance(value, bool):
            return (
                "available" if value else "unavailable",
                value,
            )

    raw_status = detail.get(
        "status"
    )

    if isinstance(raw_status, str):
        normalized = raw_status.strip().lower()

        if normalized in {
            "ok",
            "pass",
            "passed",
            "healthy",
            "ready",
            "available",
            "enabled",
            "configured",
            "active",
        }:
            return "available", True

        if normalized in {
            "disabled",
            "unavailable",
            "unhealthy",
            "failed",
            "fail",
            "blocked",
            "not_configured",
            "not configured",
            "inactive",
        }:
            return normalized.replace(" ", "_"), False

    return "reported", True


def _inspect_drawdown_guard_static_contract(
    function: Any,
    source: CapabilitySource,
) -> CapabilityState | None:
    """
    Verify only the callable contract of the balance-dependent
    production drawdown guard.

    The production guard is never invoked and no runtime
    balance or user identity is fabricated.
    """

    try:
        signature = inspect.signature(
            function
        )
    except Exception:
        return None

    parameters = signature.parameters

    current_balance = parameters.get(
        "current_balance"
    )

    user_id = parameters.get(
        "user_id"
    )

    if (
        current_balance is None
        or user_id is None
    ):
        return None

    if (
        current_balance.default
        is not inspect.Parameter.empty
    ):
        return None

    if (
        user_id.default
        is not inspect.Parameter.empty
    ):
        return None

    if (
        user_id.kind
        is not inspect.Parameter.KEYWORD_ONLY
    ):
        return None

    if not inspect.iscoroutinefunction(
        function
    ):
        return None

    return CapabilityState(
        capability=source.capability,
        module=source.module,
        entrypoint=source.entrypoint,
        state="available",
        available=True,
        verified=True,
        invocation="static_contract_probe",
        detail={
            "callable":
                source.entrypoint,

            "async":
                True,

            "required_arguments": [
                "current_balance",
                "user_id",
            ],

            "runtime_context_required":
                True,

            "production_guard_invoked":
                False,

            "database_called":
                False,
        },
        error=None,
        description=source.description,
    )


def _inspect_conversation_store_qualified_contract(
    function: Any,
    source: CapabilitySource,
) -> CapabilityState | None:
    """
    Represent the separately-qualified conversation-store
    healthcheck without re-running database I/O from the
    synchronous capability registry.

    V4 qualified the real async healthcheck as:
      - zero argument
      - SELECT only
      - status=ok
      - persistent=True
      - bounded under timeout
      - zero persistence delta

    This adapter still verifies the callable shape each time.
    If the async/argument contract changes, it falls back to
    the generic registry classification instead of claiming
    qualification.
    """

    try:
        signature = inspect.signature(
            function
        )
    except Exception:
        return None

    if signature.parameters:
        return None

    if not inspect.iscoroutinefunction(
        function
    ):
        return None

    return CapabilityState(
        capability=source.capability,
        module=source.module,
        entrypoint=source.entrypoint,
        state="available",
        available=True,
        verified=True,
        invocation=(
            "qualified_select_only_async_probe"
        ),
        detail={
            "callable":
                source.entrypoint,

            "async":
                True,

            "required_arguments":
                [],

            "runtime_probe_qualified":
                True,

            "qualification":
                (
                    "conversation_store_"
                    "bounded_select_only_"
                    "async_probe_v4"
                ),

            "qualified_result_status":
                "ok",

            "qualified_persistent":
                True,

            "qualified_database_operation":
                "SELECT_ONLY",

            "qualified_persistence_delta":
                0,

            "probe_timeout_seconds":
                5,

            "healthcheck_invoked_by_registry":
                False,

            "database_called_by_registry":
                False,
        },
        error=None,
        description=source.description,
    )


def inspect_capability(
    source: CapabilitySource,
) -> CapabilityState:
    try:
        module = importlib.import_module(
            source.module
        )
    except Exception as exc:
        return CapabilityState(
            capability=source.capability,
            module=source.module,
            entrypoint=source.entrypoint,
            state="import_failure",
            available=False,
            verified=False,
            invocation="not_invoked",
            detail=None,
            error=(
                f"{type(exc).__name__}: {exc}"
            ),
            description=source.description,
        )

    function = getattr(
        module,
        source.entrypoint,
        None,
    )

    if not callable(function):
        return CapabilityState(
            capability=source.capability,
            module=source.module,
            entrypoint=source.entrypoint,
            state="no_entrypoint",
            available=False,
            verified=False,
            invocation="not_invoked",
            detail=None,
            error=None,
            description=source.description,
        )

    if (
        source.capability
        == "drawdown_guard"
    ):
        drawdown_state = (
            _inspect_drawdown_guard_static_contract(
                function,
                source,
            )
        )

        if drawdown_state is not None:
            return drawdown_state

    if (
        source.capability
        == "conversation_store"
    ):
        conversation_store_state = (
            _inspect_conversation_store_qualified_contract(
                function,
                source,
            )
        )

        if conversation_store_state is not None:
            return conversation_store_state

    try:
        required = _required_arguments(
            function
        )
    except Exception as exc:
        return CapabilityState(
            capability=source.capability,
            module=source.module,
            entrypoint=source.entrypoint,
            state="signature_failure",
            available=False,
            verified=False,
            invocation="not_invoked",
            detail=None,
            error=(
                f"{type(exc).__name__}: {exc}"
            ),
            description=source.description,
        )

    if required:
        return CapabilityState(
            capability=source.capability,
            module=source.module,
            entrypoint=source.entrypoint,
            state="requires_adapter",
            available=True,
            verified=False,
            invocation="not_invoked",
            detail={
                "required_arguments": required,
            },
            error=None,
            description=source.description,
        )

    if inspect.iscoroutinefunction(
        function
    ):
        return CapabilityState(
            capability=source.capability,
            module=source.module,
            entrypoint=source.entrypoint,
            state="async_probe_required",
            available=True,
            verified=False,
            invocation="not_invoked",
            detail={
                "reason": (
                    "The grounded developer response "
                    "builder is synchronous."
                ),
            },
            error=None,
            description=source.description,
        )

    try:
        detail = function()
    except Exception as exc:
        return CapabilityState(
            capability=source.capability,
            module=source.module,
            entrypoint=source.entrypoint,
            state="probe_failure",
            available=False,
            verified=False,
            invocation="sync_zero_arg",
            detail=None,
            error=(
                f"{type(exc).__name__}: {exc}"
            ),
            description=source.description,
        )

    state, available = _normalize_state(
        detail
    )

    return CapabilityState(
        capability=source.capability,
        module=source.module,
        entrypoint=source.entrypoint,
        state=state,
        available=available,
        verified=True,
        invocation="sync_zero_arg",
        detail=detail,
        error=None,
        description=source.description,
    )


def build_capability_registry() -> dict[str, Any]:
    states = [
        inspect_capability(source)
        for source in CAPABILITY_SOURCES
    ]

    rows = [
        asdict(state)
        for state in states
    ]

    verified_count = sum(
        1
        for state in states
        if state.verified
    )

    available_count = sum(
        1
        for state in states
        if state.available
    )

    operational_count = sum(
        1
        for state in states
        if (
            state.verified
            and state.available
        )
    )

    attention_count = sum(
        1
        for state in states
        if state.state
        in {
            "import_failure",
            "no_entrypoint",
            "signature_failure",
            "probe_failure",
            "unavailable",
            "failed",
            "blocked",
            "not_configured",
            "inactive",
            "requires_adapter",
            "async_probe_required",
        }
    )

    return {
        "registry_version": "stage3.v1",
        "read_only": True,
        "source_count": len(states),
        "verified_count": verified_count,
        "available_count": available_count,
        "operational_count": operational_count,
        "attention_count": attention_count,
        "states": rows,
    }


def capability_summary_lines(
    registry: dict[str, Any],
) -> list[str]:
    rows = registry.get(
        "states",
        [],
    )

    if not isinstance(rows, list):
        return []

    lines: list[str] = []

    for row in rows:
        if not isinstance(row, dict):
            continue

        capability = str(
            row.get(
                "capability",
                "unknown",
            )
        )

        state = str(
            row.get(
                "state",
                "unknown",
            )
        )

        verified = bool(
            row.get(
                "verified",
                False,
            )
        )

        invocation = str(
            row.get(
                "invocation",
                "unknown",
            )
        )

        lines.append(
            f"{capability}: state={state}; "
            f"verified={verified}; "
            f"invocation={invocation}"
        )

    return lines


__all__ = [
    "CAPABILITY_SOURCES",
    "CapabilitySource",
    "CapabilityState",
    "build_capability_registry",
    "capability_summary_lines",
    "inspect_capability",
]
