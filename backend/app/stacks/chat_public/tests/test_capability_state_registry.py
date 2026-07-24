from __future__ import annotations

from backend.app.stacks.chat_public.capability_state_registry import (
    CAPABILITY_SOURCES,
    build_capability_registry,
    capability_summary_lines,
)

from backend.app.stacks.chat_public.developer_response_builder import (
    build_developer_response,
)


def test_registry_is_read_only_and_complete() -> None:
    registry = build_capability_registry()

    assert registry["read_only"] is True
    assert registry["registry_version"] == "stage3.v1"
    assert registry["source_count"] == len(
        CAPABILITY_SOURCES
    )
    assert len(registry["states"]) == len(
        CAPABILITY_SOURCES
    )


def test_registry_uses_declared_state_categories() -> None:
    registry = build_capability_registry()

    allowed_states = {
        "available",
        "unavailable",
        "reported",
        "disabled",
        "failed",
        "blocked",
        "not_configured",
        "inactive",
        "import_failure",
        "no_entrypoint",
        "signature_failure",
        "probe_failure",
        "requires_adapter",
        "async_probe_required",
    }

    for row in registry["states"]:
        assert row["state"] in allowed_states


def test_drawdown_guard_is_not_called_without_balance() -> None:
    registry = build_capability_registry()

    matching = [
        row
        for row in registry["states"]
        if row["capability"] == "drawdown_guard"
    ]

    assert len(matching) == 1

    row = matching[0]

    assert row["state"] == "requires_adapter"
    assert row["verified"] is False
    assert row["invocation"] == "not_invoked"
    assert "current_balance" in row["detail"][
        "required_arguments"
    ]


def test_registry_summary_is_grounded_in_rows() -> None:
    registry = build_capability_registry()

    lines = capability_summary_lines(
        registry
    )

    assert len(lines) == registry["source_count"]

    for line in lines:
        assert "state=" in line
        assert "verified=" in line
        assert "invocation=" in line


def test_developer_response_contains_capability_state() -> None:
    response = build_developer_response(
        subtype="self_evaluation",
    )

    assert "### Capability state" in response
    assert "market_data_provider_registry:" in response
    assert "paper_broker:" in response
    assert "snaptrade_adapter:" in response
    assert "drawdown_guard:" in response


def test_developer_capabilities_remain_grounded() -> None:
    response = build_developer_response(
        subtype="self_evaluation",
    ).lower()

    assert "broker operations occurred" in response
    assert "risk analysis capabilities are up-to-date" not in response
    assert "market analysis module is accurately" not in response
    assert "test_trading_pipeline.py" not in response


def test_unverified_adapter_and_async_states_require_attention() -> None:
    registry = build_capability_registry()

    attention_rows = [
        row
        for row in registry["states"]
        if row["state"] in {
            "requires_adapter",
            "async_probe_required",
        }
    ]

    assert len(attention_rows) == 2
    assert registry["attention_count"] >= 2

    capabilities = {
        row["capability"]
        for row in attention_rows
    }

    assert "drawdown_guard" in capabilities
    assert "conversation_store" in capabilities
