"""
Read-only connected-symbol bridge.

Provides a neutral application boundary for authenticated chat.
No brokerage credentials, provider requests, or order operations.
"""

from backend.app.stacks.snaptrade.application.connected_symbol_context import (
    get_connected_symbols_for_owner,
)


async def read_authenticated_connected_symbols(
    *,
    owner_user_id: str,
) -> list[str]:
    owner = str(owner_user_id or "").strip()
    if not owner:
        raise ValueError("Authenticated owner required")

    return await get_connected_symbols_for_owner(
        authenticated_owner_user_id=owner,
    )


async def select_authenticated_training_symbols(
    *,
    owner_user_id: str,
    owner_session_id: str,
    role: str,
    requested_symbols=None,
) -> tuple[str, ...]:
    """
    Select only connected symbols belonging to the authenticated owner.

    Does not start a training run or authorize any broker operations.
    """
    from backend.app.stacks.db_runtime.owner_ai_scope import (
        OwnerAIScope,
        select_owner_symbols,
    )

    scope = OwnerAIScope(
        owner_user_id=owner_user_id,
        owner_session_id=owner_session_id,
        role=role,
    )

    scope.authorize("connected_symbols_read")
    scope.authorize("owner_training")

    connected = await read_authenticated_connected_symbols(
        owner_user_id=scope.owner_user_id,
    )

    return select_owner_symbols(
        scope=scope,
        connected_symbols=connected,
        requested_symbols=requested_symbols,
    )


async def launch_connected_owner_training(
    *,
    owner_user_id: str,
    owner_session_id: str,
    role: str,
    duration_seconds: int = 120,
    notification_thread_id: str | None = None,
    notification_parent_message_id: str | None = None,
) -> dict:
    """Launch authenticated, filtered, historical USER training.

    Never selects SYSTEM scope or sends broker orders.
    """

    from backend.app.stacks.strategy_candidate_sandbox.L4_runtime_orchestration import (
        bounded_training_runtime as training_runtime,
    )

    if str(role).strip().lower() in {
        "admin", "administrator", "system_admin", "support"
    }:
        raise PermissionError("Training role denied")

    selected = await select_authenticated_training_symbols(
        owner_user_id=owner_user_id,
        owner_session_id=owner_session_id,
        role=role,
    )

    available = {
        str(dataset.get("symbol", "")).strip().upper()
        for dataset in training_runtime.discover_canadian_datasets()
    }

    missing = set(selected) - available

    if missing:
        raise ValueError(
            "Historical datasets missing for selected symbols"
        )

    if not 1 <= int(duration_seconds) <= 600:
        raise ValueError("Training duration outside bounded limits")

    run = training_runtime.start_bounded_training_session(
        duration_seconds=int(duration_seconds),
        universe="canada",
        requested_by=owner_user_id,
        source="authenticated_connected_snaptrade_chat",
        scope="user",
        owner_user_id=owner_user_id,
        owner_session_id=owner_session_id,
        requested_by_role=role,
        selected_symbols=tuple(selected),
        notification_thread_id=notification_thread_id,
        notification_parent_message_id=notification_parent_message_id,
    )

    if run.get("scope") != "user":
        raise RuntimeError("Unexpected training scope")

    if run.get("owner_user_id") != owner_user_id:
        raise RuntimeError("Unexpected training owner")

    return run


def get_authenticated_owner_training_result(
    *,
    owner_user_id: str,
    run_id: str,
) -> dict | None:
    """Read a USER training result belonging to the authenticated owner.

    Caller must supply the trusted server-authenticated owner identity.
    Returns None for missing or inaccessible runs.
    """
    import re

    from backend.app.stacks.strategy_candidate_sandbox.L4_runtime_orchestration import (
        bounded_training_runtime as runtime,
    )

    owner = str(owner_user_id or "").strip()
    requested_run = str(run_id or "").strip()

    if not owner:
        raise PermissionError("Authenticated owner required")

    if not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", requested_run):
        raise ValueError("Invalid training run ID")

    result = runtime.get_training_session(requested_run)

    if not isinstance(result, dict):
        return None

    if result.get("scope") != "user":
        return None

    if str(result.get("owner_user_id") or "").strip() != owner:
        return None

    return result
