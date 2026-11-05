from __future__ import annotations

import logging

LOGGER = logging.getLogger(
    "neurovest.developer_authorization"
)

VERSION = "NEUROVEST_DEVELOPER_AUTHORIZATION_3ER1"

DEV_ROLES = frozenset({
    "dev",
    "developer",
})


def _role_name(value):
    if value is None:
        return ""

    if not isinstance(value, str):
        value = getattr(value, "value", None)

    if not isinstance(value, str):
        return ""

    return value.strip().casefold()


def _verified_role(principal):
    """
    Read role information only from the authenticated
    principal constructed by the server.

    Never read role claims from chat messages,
    request JSON, model output, or prompt context.
    """
    if principal is None:
        return False

    subject = getattr(principal, "subject", None)

    if not isinstance(subject, str) or not subject.strip():
        return False

    role = _role_name(
        getattr(principal, "role", None)
    )

    if role in DEV_ROLES:
        return True

    roles = getattr(principal, "roles", None)

    if isinstance(roles, (list, tuple, frozenset, set)):
        return any(
            _role_name(item) in DEV_ROLES
            for item in roles
        )

    return False


def authorized_developer(
    *,
    principal,
    existing_permission,
):
    """
    Accept either:
    1. The already-established server-side developer
       evidence authorization, or
    2. An explicit developer role on the authenticated
       backend principal.

    Do not accept Admin as Developer automatically.

    Live trading and system execution still retain
    their own authorization and safety boundaries.
    """
    subject = getattr(principal, "subject", None)

    if not isinstance(subject, str) or not subject.strip():
        return False

    return (
        existing_permission is True
        or _verified_role(principal)
    )


def assessed_developer_reply(
    *,
    principal,
    existing_permission,
    message,
):
    from backend.app.stacks.chat_public.developer_intelligence_3e import (
        is_improvement_request,
        safe_developer_reply,
    )

    if not is_improvement_request(message):
        return None

    allowed = authorized_developer(
        principal=principal,
        existing_permission=existing_permission,
    )

    LOGGER.info(
        "neuro_developer_assessment "
        "intent=matched authorized=%s",
        allowed,
    )

    if not allowed:
        return None

    try:
        answer = safe_developer_reply(
            authorized=True,
            message=message,
        )
    except Exception as exc:
        LOGGER.error(
            "neuro_developer_assessment_failed "
            "error_type=%s",
            type(exc).__name__,
        )
        return (
            "Developer capability inspection was "
            "authorized, but the evidence inventory "
            "could not be completed. "
            "No system changes were made."
        )

    if not isinstance(answer, str) or not answer.strip():
        return (
            "Developer capability inspection returned "
            "no verified evidence. "
            "No system changes were made."
        )

    LOGGER.info(
        "neuro_developer_assessment "
        "result=grounded length=%s",
        len(answer),
    )

    return answer
