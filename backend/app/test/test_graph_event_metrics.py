from __future__ import annotations

from backend.app.core.cognitive_graph_state import (
    CognitiveGraphState,
)


def isolated_state() -> CognitiveGraphState:
    state = CognitiveGraphState()

    state.node_state.clear()
    state.node_meta.clear()
    state.edge_activity.clear()
    state.edge_meta.clear()
    state.last_events.clear()
    state.recent_flows.clear()
    state.sequence = 0

    state.save_snapshot = lambda: None  # type: ignore[method-assign]
    state.append_event = lambda event: None  # type: ignore[method-assign]

    return state


def test_node_metrics_aggregate_latency_and_success() -> None:
    state = isolated_state()

    state.activate_node(
        "authentication_runtime",
        "JWT_VALIDATED",
        {
            "layer": "L1",
            "stack": "identity_auth",
            "status": "completed",
            "http_status": 200,
            "latency_ms": 10.0,
            "payload_bytes": 100,
            "response_bytes": 250,
        },
    )

    state.activate_node(
        "authentication_runtime",
        "JWT_VALIDATED",
        {
            "layer": "L1",
            "stack": "identity_auth",
            "status": "completed",
            "http_status": 200,
            "latency_ms": 30.0,
            "payload_bytes": 50,
            "response_bytes": 150,
        },
    )

    meta = state.node_meta[
        "authentication_runtime"
    ]

    assert meta[
        "request_count"
    ] == 2

    assert meta[
        "success_count"
    ] == 2

    assert meta[
        "failure_count"
    ] == 0

    assert meta[
        "average_latency_ms"
    ] == 20.0

    assert meta[
        "minimum_latency_ms"
    ] == 10.0

    assert meta[
        "maximum_latency_ms"
    ] == 30.0

    assert meta[
        "bytes_in"
    ] == 150

    assert meta[
        "bytes_out"
    ] == 400

    assert meta[
        "health"
    ] == "healthy"


def test_security_metrics_count_unauthorized_and_forbidden() -> None:
    state = isolated_state()

    state.activate_node(
        "route_authorization",
        "AUTHORIZATION_REJECTED",
        {
            "layer": "L1",
            "stack": "identity_auth",
            "status": "unauthorized",
            "status_code": 401,
            "latency_ms": 2.5,
        },
    )

    state.activate_node(
        "route_authorization",
        "AUTHORIZATION_REJECTED",
        {
            "layer": "L1",
            "stack": "identity_auth",
            "status": "forbidden",
            "status_code": 403,
            "latency_ms": 3.5,
        },
    )

    meta = state.node_meta[
        "route_authorization"
    ]

    assert meta[
        "failure_count"
    ] == 2

    assert meta[
        "unauthorized_count"
    ] == 1

    assert meta[
        "forbidden_count"
    ] == 1

    assert meta[
        "http_error_count"
    ] == 2

    assert meta[
        "health"
    ] == "degraded"


def test_edge_metrics_are_aggregated() -> None:
    state = isolated_state()

    state.activate_edge(
        "frontend_dashboard",
        "analytics_api",
        {
            "status": "completed",
            "http_status": 200,
            "latency_ms": 12.0,
            "payload_bytes": 20,
            "response_bytes": 500,
        },
    )

    state.activate_edge(
        "frontend_dashboard",
        "analytics_api",
        {
            "status": "failed",
            "http_status": 500,
            "latency_ms": 28.0,
            "payload_bytes": 20,
            "response_bytes": 100,
        },
    )

    meta = state.edge_meta[
        "frontend_dashboard->analytics_api"
    ]

    assert meta[
        "count"
    ] == 2

    assert meta[
        "request_count"
    ] == 2

    assert meta[
        "success_count"
    ] == 1

    assert meta[
        "failure_count"
    ] == 1

    assert meta[
        "average_latency_ms"
    ] == 20.0

    assert meta[
        "http_error_count"
    ] == 1


def test_snapshot_advertises_metric_contract_version_two() -> None:
    state = isolated_state()

    snapshot = state.snapshot()

    assert snapshot[
        "contract"
    ][
        "version"
    ] == 2

    assert snapshot[
        "contract"
    ][
        "metric_aggregation"
    ] is True

    assert (
        "p95_latency_ms"
        in snapshot[
            "contract"
        ][
            "supported_metrics"
        ]
    )
