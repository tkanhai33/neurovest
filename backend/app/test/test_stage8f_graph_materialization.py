from __future__ import annotations

from backend.app.core.cognitive_graph_state import (
    CognitiveGraphState,
    DECLARED_GRAPH_EDGES,
    NODE_ARCHITECTURE,
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


def test_all_layers_have_declared_nodes() -> None:
    layers = {
        ownership.get(
            "layer"
        )
        for ownership in NODE_ARCHITECTURE.values()
    }

    assert {
        "L7",
        "L6",
        "L5",
        "L4",
        "L3",
        "L2",
        "L1",
        "L0",
    } <= layers


def test_required_facades_are_declared_in_l3() -> None:
    required = {
        "authentication_facade",
        "chat_facade",
        "conversation_facade",
        "market_data_facade",
        "portfolio_facade",
        "risk_facade",
        "strategy_facade",
        "decision_audit_query_facade",
    }

    for node in required:
        assert (
            NODE_ARCHITECTURE[
                node
            ][
                "layer"
            ]
            == "L3"
        )


def test_frontend_workspaces_and_proxies_are_declared() -> None:
    required = {
        "dashboard_shell",
        "overview_workspace",
        "market_workspace",
        "graph_workspace",
        "observability_workspace",
        "learning_workspace",
        "neuro_workspace",
        "chat_proxy",
        "graph_proxy",
        "market_proxy",
        "portfolio_proxy",
        "risk_proxy",
        "strategy_proxy",
    }

    for node in required:
        assert (
            NODE_ARCHITECTURE[
                node
            ][
                "layer"
            ]
            == "L6"
        )


def test_snapshot_materializes_declared_topology_without_events() -> None:
    state = isolated_state()

    snapshot = state.snapshot()

    assert snapshot[
        "sequence"
    ] == 0

    assert snapshot[
        "events"
    ] == []

    assert snapshot[
        "recent_flows"
    ] == []

    assert len(
        snapshot[
            "nodes"
        ]
    ) == len(
        NODE_ARCHITECTURE
    )

    assert len(
        snapshot[
            "edges"
        ]
    ) == len(
        DECLARED_GRAPH_EDGES
    )

    assert all(
        count == 0
        for count in snapshot[
            "edges"
        ].values()
    )

    assert all(
        meta[
            "observed"
        ]
        is False
        for meta in snapshot[
            "node_meta"
        ].values()
    )


def test_real_node_activation_overrides_declared_state() -> None:
    state = isolated_state()

    state.activate_node(
        "market_data_facade",
        "MARKET_FACADE_CALLED",
        {
            "status": "completed",
            "latency_ms": 8.0,
            "success": True,
        },
    )

    snapshot = state.snapshot()

    node = snapshot[
        "node_meta"
    ][
        "market_data_facade"
    ]

    assert node[
        "declared"
    ] is True

    assert node[
        "observed"
    ] is True

    assert node[
        "materialization_state"
    ] == "observed"

    assert node[
        "request_count"
    ] == 1

    assert node[
        "average_latency_ms"
    ] == 8.0


def test_real_edge_materializes_both_endpoints() -> None:
    state = isolated_state()

    state.activate_edge(
        "runtime_source",
        "runtime_destination",
        {
            "status": "completed",
            "latency_ms": 3.0,
            "success": True,
        },
    )

    snapshot = state.snapshot()

    for node in (
        "runtime_source",
        "runtime_destination",
    ):
        meta = snapshot[
            "node_meta"
        ][
            node
        ]

        assert meta[
            "observed"
        ] is True

        assert meta[
            "materialized_from_edge"
        ] is True

        assert meta[
            "request_count"
        ] == 0

    edge = snapshot[
        "edge_meta"
    ][
        "runtime_source->runtime_destination"
    ]

    assert edge[
        "observed"
    ] is True

    assert edge[
        "request_count"
    ] == 1


def test_declared_edge_becomes_observed_without_losing_relation() -> None:
    state = isolated_state()

    state.activate_edge(
        "chat_proxy",
        "chat_api",
        {
            "status": "completed",
            "success": True,
        },
    )

    snapshot = state.snapshot()

    edge = snapshot[
        "edge_meta"
    ][
        "chat_proxy->chat_api"
    ]

    assert edge[
        "declared"
    ] is True

    assert edge[
        "observed"
    ] is True

    assert edge[
        "relation"
    ] == "forwards"

    assert edge[
        "request_count"
    ] == 1


def test_stage8f_preserves_version_two_contract() -> None:
    snapshot = isolated_state().snapshot()

    contract = snapshot[
        "contract"
    ]

    assert contract[
        "version"
    ] == 2

    assert contract[
        "declared_topology"
    ] is True

    assert contract[
        "edge_endpoint_materialization"
    ] is True

    assert contract[
        "synthetic_activations"
    ] is False

    assert (
        contract[
            "declared_edges_are_runtime_activity"
        ]
        is False
    )
