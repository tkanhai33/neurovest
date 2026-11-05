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


def test_drawdown_guard_uses_static_contract_probe_without_invocation() -> None:
    registry = build_capability_registry()

    matching = [
        row
        for row in registry["states"]
        if row["capability"] == "drawdown_guard"
    ]

    assert len(matching) == 1

    row = matching[0]

    assert row["state"] == "available"
    assert row["available"] is True
    assert row["verified"] is True

    assert (
        row["invocation"]
        == "static_contract_probe"
    )

    assert (
        row["detail"]["callable"]
        == "healthcheck"
    )

    assert (
        row["detail"]["async"]
        is True
    )

    assert (
        row["detail"][
            "runtime_context_required"
        ]
        is True
    )

    assert (
        row["detail"][
            "production_guard_invoked"
        ]
        is False
    )

    assert (
        row["detail"][
            "database_called"
        ]
        is False
    )

    assert (
        row["detail"][
            "required_arguments"
        ]
        == [
            "current_balance",
            "user_id",
        ]
    )


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

    assert attention_rows == []

    assert (
        registry["attention_count"]
        == 0
    )


def test_conversation_store_uses_qualified_async_probe_without_runtime_invocation() -> None:
    registry = build_capability_registry()

    matching = [
        row
        for row in registry["states"]
        if row["capability"]
        == "conversation_store"
    ]

    assert len(matching) == 1

    row = matching[0]

    assert row["state"] == "available"
    assert row["available"] is True
    assert row["verified"] is True

    assert (
        row["invocation"]
        == "qualified_select_only_async_probe"
    )

    assert (
        row["detail"]["callable"]
        == "healthcheck"
    )

    assert (
        row["detail"]["async"]
        is True
    )

    assert (
        row["detail"]["required_arguments"]
        == []
    )

    assert (
        row["detail"][
            "runtime_probe_qualified"
        ]
        is True
    )

    assert (
        row["detail"][
            "qualified_result_status"
        ]
        == "ok"
    )

    assert (
        row["detail"][
            "qualified_persistent"
        ]
        is True
    )

    assert (
        row["detail"][
            "qualified_database_operation"
        ]
        == "SELECT_ONLY"
    )

    assert (
        row["detail"][
            "healthcheck_invoked_by_registry"
        ]
        is False
    )

    assert (
        row["detail"][
            "database_called_by_registry"
        ]
        is False
    )
