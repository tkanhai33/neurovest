from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any

from backend.app.core.cognitive_graph_state import (
    graph_state,
)


class CognitiveEventBus:
    def __init__(
        self,
    ) -> None:
        self.listeners: defaultdict[
            str,
            list,
        ] = defaultdict(
            list
        )

    def subscribe(
        self,
        event_type: str,
        fn,
    ) -> None:
        self.listeners[
            event_type
        ].append(
            fn
        )

    async def emit(
        self,
        event_type: str,
        payload: dict[str, Any],
    ) -> None:
        """
        Dispatch one event and preserve its complete observability
        payload through the cognitive graph boundary.
        """

        normalized_payload = dict(
            payload or {}
        )

        if event_type in self.listeners:
            await asyncio.gather(
                *[
                    fn(
                        normalized_payload
                    )
                    for fn in self.listeners[
                        event_type
                    ]
                ],
                return_exceptions=True,
            )

        source = str(
            normalized_payload.get(
                "from",
                "unknown",
            )
        )

        destination = str(
            normalized_payload.get(
                "to",
                "unknown",
            )
        )

        node = str(
            normalized_payload.get(
                "node",
                source,
            )
        )

        graph_state.activate_node(
            node,
            event_type,
            normalized_payload,
        )

        if (
            source != "unknown"
            and destination != "unknown"
        ):
            edge_payload = {
                **normalized_payload,
                "event_type": event_type,
            }

            graph_state.activate_edge(
                source,
                destination,
                edge_payload,
            )


event_bus = CognitiveEventBus()
