from __future__ import annotations

from pathlib import Path

from backend.app.core.cognitive_graph_state import (
    NODE_ARCHITECTURE,
)

from backend.app.core.runtime_trace import (
    emit_runtime_step,
)

from backend.app.stacks.events.broker import (
    global_event_bus,
)


def test_stage8e_architecture_nodes_are_registered() -> None:
    expected = {
        "frontend_chat": "L6",
        "chat_api": "L5",
        "chat_runtime": "L4",
        "conversation_store": "L3",
        "context_assembler": "L2",
        "jwt_validation": "L1",
        "route_authorization": "L1",
        "postgresql_adapter": "L0",
        "ollama_adapter": "L0",
    }

    for node, layer in expected.items():
        assert (
            NODE_ARCHITECTURE[
                node
            ][
                "layer"
            ]
            == layer
        )


def test_runtime_trace_supports_stage8d_metrics() -> None:
    source = Path(
        "backend/app/core/runtime_trace.py"
    ).read_text(
        encoding="utf-8"
    )

    for field in (
        "http_status",
        "latency_ms",
        "payload_bytes",
        "response_bytes",
        "success",
        "error",
    ):
        assert field in source


def test_chat_runtime_contains_required_operational_stages() -> None:
    source = Path(
        "backend/app/stacks/chat_public/"
        "chat_runtime.py"
    ).read_text(
        encoding="utf-8"
    )

    required = (
        "CHAT_RUNTIME_STARTED",
        "CONVERSATION_LOOKUP_STARTED",
        "POSTGRESQL_THREAD_READY",
        "USER_MESSAGE_PERSISTED",
        "CONTEXT_ASSEMBLY_STARTED",
        "MEMORY_CONTEXT_ASSEMBLED",
        "INTENT_CLASSIFICATION_STARTED",
        "INTENT_CLASSIFICATION_COMPLETED",
        "OLLAMA_RESPONSE_RECEIVED",
        "RESPONSE_VALIDATED",
        "ASSISTANT_MESSAGE_PERSISTED",
        "SUMMARY_MEMORY_UPDATED",
        "CHAT_RUNTIME_COMPLETED",
    )

    for event_type in required:
        assert event_type in source

    prohibited = (
        '"raw_prompt"',
        '"jwt"',
        '"password"',
        '"chain_of_thought"',
        '"hidden_reasoning"',
    )

    for value in prohibited:
        assert value not in source


def test_route_policy_emits_security_events() -> None:
    source = Path(
        "backend/app/stacks/identity_auth/"
        "route_protection.py"
    ).read_text(
        encoding="utf-8"
    )

    for event_type in (
        "HTTP_REQUEST_RECEIVED",
        "JWT_VALIDATION_STARTED",
        "JWT_VALIDATION_COMPLETED",
        "JWT_VALIDATION_REJECTED",
        "ADMIN_AUTHORIZATION_REJECTED",
        "HTTP_REQUEST_COMPLETED",
    ):
        assert event_type in source


def test_frontend_preserves_playback_and_exposes_metrics() -> None:
    panel = Path(
        "frontend/app/components/workspaces/"
        "GraphWorkspacePanel.tsx"
    ).read_text(
        encoding="utf-8"
    )

    service = Path(
        "frontend/services/graphService.ts"
    ).read_text(
        encoding="utf-8"
    )

    assert "neurovest-graph-node-pulse" in panel
    assert "neurovest-graph-edge-pulse" in panel
    assert "average_latency_ms" in panel
    assert "p95_latency_ms" in panel
    assert "request_count" in service
    assert "supported_metrics" in service


def test_global_event_bus_remains_canonical() -> None:
    assert global_event_bus is not None
    assert callable(emit_runtime_step)
