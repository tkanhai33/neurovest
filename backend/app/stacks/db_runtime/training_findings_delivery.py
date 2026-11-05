
"""Persist evidence-grounded training findings to the owner's chat."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)

# NEUROVEST_TRAINING_FINDINGS_LOOP_REPAIR_V1
# Capture the serving event loop before launching the worker.
# PostgreSQL's async engine must not be used from an unrelated loop.
_delivery_loop = None


def register_training_findings_loop() -> None:
    global _delivery_loop
    loop = asyncio.get_running_loop()
    if loop.is_closed() or not loop.is_running():
        raise RuntimeError("Application event loop unavailable")
    _delivery_loop = loop


def _delivery_finished(future, run_id: str) -> None:
    try:
        delivered = future.result()
        if delivered:
            logger.info(
                "Training findings delivered for %s", run_id
            )
        else:
            logger.info(
                "Training findings skipped for %s", run_id
            )
    except Exception:
        logger.exception(
            "Training findings delivery failed for %s",
            run_id,
        )



def format_training_findings(record: dict[str, Any]) -> str:
    status = str(record.get("status") or "")
    if status not in {"completed", "failed"}:
        raise ValueError("Training is not in a terminal state")

    run_id = str(record.get("run_id") or "")
    if not run_id:
        raise ValueError("Training run identifier required")

    lines = [
        "Neuro — Personal Training Findings",
        "",
        f"Training status: {status.upper()}",
        f"Run ID: {run_id}",
        "Scope: Your personal training profile",
    ]

    symbols = record.get("symbols") or record.get(
        "selected_symbols"
    ) or []

    if symbols:
        lines.append(
            "Symbols: " + ", ".join(str(s) for s in symbols)
        )

    for key, title in (
        ("eligible_symbol_count", "Eligible symbols"),
        ("rows_evaluated", "Historical rows evaluated"),
        ("cycles", "Evaluation cycles"),
    ):
        value = record.get(key)
        if value is not None:
            lines.append(f"{title}: {value}")

    if status == "failed":
        lines.append(
            "Training did not complete successfully."
        )
        if record.get("error"):
            lines.append(
                "Recorded reason: " + str(record["error"])[:350]
            )
    else:
        contribution = record.get(
            "sanitized_learning_contribution"
        )
        if not isinstance(contribution, dict):
            contribution = {}

        for key, title in (
            ("aggregate_reward", "Aggregate reward"),
            ("reward", "Reward"),
            ("average_reward", "Average reward"),
            ("average_confidence", "Average confidence"),
            ("confidence", "Confidence score"),
            ("confidence_score", "Confidence score"),
        ):
            value = record.get(key)
            if value is None:
                value = contribution.get(key)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                lines.append(f"{title}: {value}")

        lines.extend([
            "",
            "Findings:",
            "The historical evaluation completed. "
            "The numbers above are recorded training metrics, "
            "not predictions of future returns.",
            "A negative reward, when recorded, indicates "
            "underperformance under the runtime's reward definition. "
            "It does not by itself identify the cause.",
            "Confidence is an internal model metric, "
            "not a guaranteed probability of profitable trading.",
        ])

    lines.extend([
        "",
        "No live brokerage orders were placed by this training run.",
        "Your personal training remains separate from global training.",
        "",
        "You can ask me to explain the metrics or investigate "
        "the individual symbol results.",
    ])

    return "\n".join(lines)


async def deliver_training_findings(
    record: dict[str, Any],
) -> bool:
    if record.get("scope") != "user":
        return False

    owner = str(record.get("owner_user_id") or "").strip()
    thread_id = str(
        record.get("notification_thread_id") or ""
    ).strip()
    parent_id = str(
        record.get("notification_parent_message_id") or ""
    ).strip()
    run_id = str(record.get("run_id") or "").strip()

    if not all((owner, thread_id, parent_id, run_id)):
        return False

    from backend.app.stacks.chat_public.chat_runtime import (
        conversation_store,
    )

    thread = await conversation_store.require_thread(thread_id)

    # Fail closed if the saved conversation does not belong to
    # the account that initiated the training.
    if str(getattr(thread, "user_id", "") or "") != owner:
        raise PermissionError("Training conversation owner mismatch")

    client_id = "training-findings-" + run_id

    existing = await conversation_store.get_message_by_client_id(
        thread_id=thread_id,
        client_message_id=client_id,
    )

    if existing is not None:
        return False

    await conversation_store.append_message(
        thread_id=thread_id,
        parent_message_id=parent_id,
        role="assistant",
        content=format_training_findings(record),
        client_message_id=client_id,
        intent="connected_owner_training_findings",
        provider="neurovest_bounded_training_runtime",
        metadata={
            "source": "training_completion",
            "training_run_id": run_id,
            "training_scope": "user",
            "training_status": record.get("status"),
            "evidence_grounded": True,
        },
    )

    return True


def dispatch_training_findings(record: dict[str, Any]) -> None:
    """Schedule DB delivery on the serving application's event loop."""
    run_id = str(record.get("run_id") or "")
    loop = _delivery_loop

    if loop is None or loop.is_closed() or not loop.is_running():
        logger.error(
            "Training findings event loop unavailable for %s",
            run_id,
        )
        return

    try:
        future = asyncio.run_coroutine_threadsafe(
            deliver_training_findings(record),
            loop,
        )
        future.add_done_callback(
            lambda completed: _delivery_finished(
                completed, run_id
            )
        )
    except Exception:
        logger.exception(
            "Training findings scheduling failed for %s",
            run_id,
        )
