from __future__ import annotations

from backend.app.core.cognitive_graph_state import (
    NODE_ARCHITECTURE,
    graph_state,
)


EXPECTED = {
    "external_client": (
        "L6",
        "external",
    ),
    "chat_public": (
        "L5",
        "chat_public",
    ),
    "events_broker": (
        "L4",
        "events",
    ),
    "portfolio_reconciliation": (
        "L2",
        "portfolio",
    ),
    "repo_memory": (
        "L2",
        "memory",
    ),
    "research_db": (
        "L0",
        "research",
    ),
}


def test_historical_nodes_have_explicit_ownership() -> None:
    for node, (
        expected_layer,
        expected_stack,
    ) in EXPECTED.items():
        ownership = NODE_ARCHITECTURE[
            node
        ]

        assert ownership[
            "layer"
        ] == expected_layer

        assert ownership[
            "stack"
        ] == expected_stack


def test_historical_nodes_do_not_materialize_as_unassigned() -> None:
    snapshot = graph_state.snapshot()

    node_meta = snapshot[
        "node_meta"
    ]

    for node, (
        expected_layer,
        _,
    ) in EXPECTED.items():
        assert node in node_meta

        assert node_meta[
            node
        ][
            "layer"
        ] == expected_layer

        assert (
            node_meta[
                node
            ][
                "layer"
            ]
            != "UNASSIGNED"
        )


def test_graph_contains_no_unassigned_nodes() -> None:
    snapshot = graph_state.snapshot()

    unassigned = {
        node
        for node, meta
        in snapshot[
            "node_meta"
        ].items()
        if meta.get(
            "layer"
        )
        == "UNASSIGNED"
    }

    assert unassigned == set()


def test_contract_version_two_is_preserved() -> None:
    snapshot = graph_state.snapshot()

    assert snapshot[
        "contract"
    ][
        "version"
    ] == 2

    assert (
        snapshot[
            "contract"
        ][
            "synthetic_activations"
        ]
        is False
    )
