"""
Phase 133B runtime-flow trace helpers.

This module only reports events through the existing SystemEventBus.
It does not execute trades, mutate strategy decisions, or bypass risk.
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from backend.app.stacks.events.broker import global_event_bus


def create_trace_id(prefix: str = "runtime") -> str:
    return f"{prefix}-{uuid4().hex}"


async def emit_runtime_step(
    *,
    trace_id: str,
    event_type: str,
    node: str,
    source: str | None = None,
    destination: str | None = None,
    status: str = "active",
    symbol: str | None = None,
    message: str | None = None,
    layer: str | None = None,
    stack: str | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "trace_id": trace_id,
        "node": node,
        "status": status,
        "symbol": symbol,
        "message": message,
    }

    if source:
        payload["from"] = source

    if destination:
        payload["to"] = destination

    if layer:
        payload["layer"] = layer

    if stack:
        payload["stack"] = stack

    if details:
        safe_details = dict(details)

        payload["details"] = safe_details

        for field in (
            "http_status",
            "status_code",
            "latency_ms",
            "duration_ms",
            "payload_bytes",
            "response_bytes",
            "bytes_in",
            "bytes_out",
            "request_id",
            "user_id",
            "active_requests",
            "success",
            "error",
            "policy",
            "provider",
            "model",
            "operation",
        ):
            if field in safe_details:
                payload[field] = safe_details[field]

    return await global_event_bus.emit(
        event_type,
        payload,
    )
