
"""Fail-closed owner-scoped AI capability and symbol-selection contracts."""

from dataclasses import dataclass
import re


SYMBOL_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9.^_-]{0,31}$")

USER_CAPABILITIES = frozenset({
    "general_chat",
    "personal_memory",
    "portfolio_read",
    "connected_symbols_read",
    "market_research",
    "historical_analysis",
    "paper_simulation",
    "owner_training",
    "owner_training_results",
    "strategy_research",
})

DEVELOPER_CAPABILITIES = USER_CAPABILITIES | frozenset({
    "global_training",
    "global_research_review",
    "strategy_candidate_review",
})

FORBIDDEN_CAPABILITIES = frozenset({
    "live_broker_order",
    "broker_order_cancel",
    "broker_trade_execution",
    "global_private_data_export",
    "automatic_global_promotion",
})


class OwnerScopeDenied(PermissionError):
    pass


@dataclass(frozen=True)
class OwnerAIScope:
    owner_user_id: str
    owner_session_id: str
    role: str

    def __post_init__(self):
        if not self.owner_user_id.strip():
            raise OwnerScopeDenied("Authenticated owner required")
        if not self.owner_session_id.strip():
            raise OwnerScopeDenied("Authenticated session required")

    def authorize(self, capability: str) -> None:
        if capability in FORBIDDEN_CAPABILITIES:
            raise OwnerScopeDenied("Capability prohibited")

        allowed = (
            DEVELOPER_CAPABILITIES
            if self.role.lower() in {"developer", "owner", "dev"}
            else USER_CAPABILITIES
        )

        if capability not in allowed:
            raise OwnerScopeDenied("Capability not authorized")

    def assert_owner(self, requested_owner_id: str) -> None:
        if requested_owner_id != self.owner_user_id:
            raise OwnerScopeDenied("Cross-account access denied")


def normalize_symbols(symbols) -> tuple[str, ...]:
    result = set()

    for raw in symbols:
        symbol = str(raw).strip().upper()

        if not SYMBOL_PATTERN.fullmatch(symbol):
            raise ValueError("Invalid stock symbol")

        result.add(symbol)

    return tuple(sorted(result))


def select_owner_symbols(
    *,
    scope: OwnerAIScope,
    connected_symbols,
    requested_symbols=None,
) -> tuple[str, ...]:
    scope.authorize("owner_training")

    connected = set(normalize_symbols(connected_symbols))

    if not connected:
        raise OwnerScopeDenied("No connected symbols available")

    if requested_symbols is None:
        selected = connected
    else:
        selected = set(normalize_symbols(requested_symbols))

    if not selected:
        raise OwnerScopeDenied("No symbols selected")

    if not selected.issubset(connected):
        raise OwnerScopeDenied("Requested symbols are not connected")

    return tuple(sorted(selected))
