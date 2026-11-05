"""Developer authority from the trusted authenticated principal."""

from __future__ import annotations

from collections.abc import Mapping


def authenticated_developer_role(principal) -> bool:
    if principal is None:
        return False

    subject = getattr(principal, "subject", None)
    claims = getattr(principal, "claims", None)

    if not isinstance(subject, str) or not subject.strip():
        return False

    if not isinstance(claims, Mapping):
        return False

    role = claims.get("authorization_role") or claims.get("role")
    return (
        isinstance(role, str)
        and role.strip().lower() == "developer"
    )
