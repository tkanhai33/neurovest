
import pytest

from backend.app.stacks.db_runtime.owner_ai_scope import (
    OwnerAIScope,
    OwnerScopeDenied,
    normalize_symbols,
    select_owner_symbols,
)


def scope(owner="user-a", role="user"):
    return OwnerAIScope(
        owner_user_id=owner,
        owner_session_id="session-a",
        role=role,
    )


def test_general_ai_allowed():
    scope().authorize("general_chat")


def test_financial_research_allowed():
    scope().authorize("market_research")


def test_owner_training_allowed():
    scope().authorize("owner_training")


def test_global_training_denied_for_user():
    with pytest.raises(OwnerScopeDenied):
        scope().authorize("global_training")


def test_developer_global_training_allowed():
    scope(role="developer").authorize("global_training")


def test_live_orders_always_denied():
    with pytest.raises(OwnerScopeDenied):
        scope(role="developer").authorize("live_broker_order")


def test_cross_account_denied():
    with pytest.raises(OwnerScopeDenied):
        scope().assert_owner("user-b")


def test_owner_identity_required():
    with pytest.raises(OwnerScopeDenied):
        scope(owner="")


def test_session_identity_required():
    with pytest.raises(OwnerScopeDenied):
        OwnerAIScope("user-a", "", "user")


def test_symbol_normalization():
    assert normalize_symbols(["wcp.to", "TD.TO", "wcp.to"]) == (
        "TD.TO", "WCP.TO"
    )


def test_all_connected_symbols_selected():
    result = select_owner_symbols(
        scope=scope(),
        connected_symbols=["BTE.TO", "TD.TO", "WCP.TO"],
    )
    assert result == ("BTE.TO", "TD.TO", "WCP.TO")


def test_requested_subset_selected():
    result = select_owner_symbols(
        scope=scope(),
        connected_symbols=["BTE.TO", "TD.TO", "WCP.TO"],
        requested_symbols=["td.to"],
    )
    assert result == ("TD.TO",)


def test_unconnected_symbol_denied():
    with pytest.raises(OwnerScopeDenied):
        select_owner_symbols(
            scope=scope(),
            connected_symbols=["TD.TO"],
            requested_symbols=["AAPL"],
        )


def test_empty_holdings_denied():
    with pytest.raises(OwnerScopeDenied):
        select_owner_symbols(
            scope=scope(),
            connected_symbols=[],
        )


def test_invalid_symbol_denied():
    with pytest.raises(ValueError):
        normalize_symbols(["BAD;DROP TABLE"])


def test_unknown_capability_denied():
    with pytest.raises(OwnerScopeDenied):
        scope().authorize("unknown_capability")
