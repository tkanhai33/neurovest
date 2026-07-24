"""
DOMAIN_LOGIC_V1 asynchronous system event bus and message routing layer.

Phase 133B extends emitted events with trace correlation while preserving
the existing subscriber contract.
"""

from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable
from uuid import uuid4


Subscriber = Callable[
    [dict[str, Any]],
    Awaitable[Any],
]


def new_trace_id() -> str:
    return f"trace-{uuid4().hex}"


class SystemEventBus:
    def __init__(self) -> None:
        self._subscribers: set[Subscriber] = set()

    def subscribe(
        self,
        callback_func: Subscriber,
    ) -> None:
        self._subscribers.add(callback_func)

    def unsubscribe(
        self,
        callback_func: Subscriber,
    ) -> None:
        self._subscribers.discard(callback_func)

    async def emit(
        self,
        event_type: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        normalized_payload = dict(payload)

        normalized_payload.setdefault(
            "trace_id",
            new_trace_id(),
        )
        normalized_payload.setdefault(
            "status",
            "active",
        )
        normalized_payload.setdefault(
            "event_type",
            event_type,
        )

        event_message = {
            "event_type": event_type,
            "trace_id": normalized_payload["trace_id"],
            "payload": normalized_payload,
        }

        if self._subscribers:
            await asyncio.gather(
                *[
                    subscriber(event_message)
                    for subscriber in tuple(
                        self._subscribers
                    )
                ],
                return_exceptions=True,
            )

        return event_message


global_event_bus = SystemEventBus()


async def _graph_listener(
    event_message: dict[str, Any],
) -> None:
    from backend.app.core.cognitive_graph_state import (
        graph_state,
    )

    event_type = str(
        event_message.get(
            "event_type",
            "UNKNOWN",
        )
    )

    payload = dict(
        event_message.get("payload") or {}
    )

    payload.setdefault(
        "trace_id",
        event_message.get("trace_id")
        or new_trace_id(),
    )
    payload.setdefault(
        "event_type",
        event_type,
    )

    node = str(
        payload.get("node")
        or payload.get("to")
        or payload.get("from")
        or "unknown"
    )

    graph_state.activate_node(
        node,
        event_type,
        payload,
    )

    source = payload.get("from")
    destination = payload.get("to")

    if source and destination:
        graph_state.activate_edge(
            str(source),
            str(destination),
            payload,
        )


global_event_bus.subscribe(_graph_listener)
