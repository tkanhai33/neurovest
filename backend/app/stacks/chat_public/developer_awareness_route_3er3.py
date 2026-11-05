from __future__ import annotations

from backend.app.stacks.chat_public.developer_intelligence_3e import (
    is_improvement_request,
)

VERSION = "NEUROVEST_DEVELOPER_AWARENESS_ROUTE_3ER3"


def route_message(
    *,
    message: str,
    verified_developer: bool,
    legacy_route: str | None = None,
) -> str:
    """
    Convert a recognized self-assessment request to the
    established developer-awareness command internally.

    Authorization is NOT granted here.

    The caller must derive verified_developer from the
    existing server-side authenticated developer guard.
    The awareness engine still verifies developer access
    and thread ownership before releasing evidence.
    """
    if not isinstance(message, str):
        return ""

    if (
        verified_developer is True
        and is_improvement_request(message)
    ):
        return (
            "/dev awareness explain "
            + message.strip()
        )

    if isinstance(legacy_route, str) and legacy_route.strip():
        return legacy_route.strip()

    return message.strip()
