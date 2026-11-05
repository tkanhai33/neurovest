
"""Owner-scoped, evidence-grounded training explanations.

No brokerage orders, model training, or global profile writes.
"""

from __future__ import annotations

import re
from typing import Any

from backend.app.stacks.db_runtime.connected_symbol_context_bridge import (
    get_authenticated_owner_training_result,
)

RUN_PATTERN = re.compile(
    r"\btraining_[A-Za-z0-9_-]{1,119}\b"
)

TRAINING_TERMS = (
    "training",
    "trained",
    "reward",
    "confidence",
    "evaluation",
    "learning run",
    "last run",
    "previous run",
    "which stock",
    "which symbol",
)

QUESTION_TERMS = (
    "why",
    "how",
    "explain",
    "what",
    "result",
    "performance",
    "compare",
    "best",
    "worst",
    "meaning",
    "mean",
    "analy",
    "summar",
)

def is_training_followup(message: str) -> bool:
    value = message.casefold().strip()

    # NEUROVEST_RESPONSE_ROUTING_REPAIR_V2
    # A global/system-training question is not a request
    # to explain a previous personal training session.
    from backend.app.stacks.chat_public.global_training_intent_guard import (
        classify_global_training_request,
    )

    global_intent = classify_global_training_request(value)

    if global_intent.classification != "not_global_training":
        return False

    # Additional system-training phrasing is discussion,
    # not evidence retrieval for a personal run.
    if re.search(
        r"\bsystem\s+training\b",
        value,
    ):
        return False

    if RUN_PATTERN.search(value):
        return True

    return (
        any(term in value for term in TRAINING_TERMS)
        and any(term in value for term in QUESTION_TERMS)
    )

def choose_run_id(
    message: str,
    conversation_messages: list[Any],
) -> str | None:
    explicit = RUN_PATTERN.search(message)

    if explicit:
        return explicit.group(0)

    for item in reversed(conversation_messages):
        content = str(getattr(item, "content", "") or "")
        match = RUN_PATTERN.search(content)

        if match:
            return match.group(0)

    return None

def _number(value: Any) -> float | None:
    try:
        if value is None or isinstance(value, bool):
            return None
        return float(value)
    except (TypeError, ValueError, OverflowError):
        return None

def explain_training(
    record: dict[str, Any],
    message: str,
) -> str:
    run_id = str(record.get("run_id") or "unknown")
    status = str(record.get("status") or "unknown")

    if status != "completed":
        return (
            f"Training run {run_id} is currently {status}. "
            "A final performance explanation is unavailable "
            "until the run completes."
        )

    contribution = (
        record.get("sanitized_learning_contribution") or {}
    )

    rows = record.get("rows_evaluated")
    cycles = record.get("cycles")

    if rows is None:
        rows = contribution.get("rows_evaluated")

    if cycles is None:
        cycles = contribution.get("cycles")

    reward = _number(contribution.get("average_reward"))
    confidence = _number(
        contribution.get("average_confidence")
    )

    symbols = (
        record.get("selected_symbols")
        or record.get("symbols")
        or []
    )

    if not isinstance(symbols, list):
        symbols = []

    lines = [
        "Neuro — Training Analysis",
        "",
        f"Run: {run_id}",
        "Scope: Your personal training profile",
    ]

    if symbols:
        lines.append(
            "Symbols: " + ", ".join(map(str, symbols))
        )

    if rows is not None:
        lines.append(
            f"Historical rows evaluated: {rows}"
        )

    if cycles is not None:
        lines.append(
            f"Evaluation cycles: {cycles}"
        )

    lines.extend(["", "Interpretation:"])

    if reward is None:
        lines.append(
            "The available evidence does not contain "
            "a verified average reward."
        )
    elif reward < 0:
        lines.append(
            f"Average reward was {reward:.8f}. "
            "This is negative under the runtime's reward "
            "definition, indicating average underperformance "
            "against that internal objective. It is not "
            "automatically a portfolio return or realized loss."
        )
    elif reward > 0:
        lines.append(
            f"Average reward was {reward:.8f}. "
            "This is positive under the runtime's reward "
            "definition, but does not establish live "
            "profitability or future performance."
        )
    else:
        lines.append(
            "Average reward was zero under the recorded "
            "runtime reward definition."
        )

    if confidence is not None:
        lines.append(
            f"Average confidence was {confidence:.8f}. "
            "This is an internal model confidence metric, "
            "not a calibrated probability of a profitable trade."
        )
    else:
        lines.append(
            "Verified average confidence was unavailable."
        )

    question = message.casefold()

    if any(
        term in question
        for term in (
            "why", "cause", "reason", "negative",
            "underperform",
        )
    ):
        lines.extend([
            "",
            "Why the reward was negative:",
            "The aggregate reward alone cannot identify "
            "which decisions, symbols, or market conditions "
            "caused the result. That requires recorded "
            "per-cycle or per-symbol attribution evidence.",
        ])

    if any(
        term in question
        for term in (
            "which stock", "which symbol",
            "best", "worst", "compare",
            "individual symbol",
        )
    ):
        lines.extend([
            "",
            "Individual stock comparison:",
            "The verified aggregate metrics do not establish "
            "which symbol performed best or worst. I will "
            "not rank stocks without recorded per-symbol "
            "evaluation evidence.",
        ])

    lines.extend([
        "",
        "These are historical simulation metrics, "
        "not predictions or evidence of live trading profits.",
        "No brokerage execution is required to review them.",
    ])

    return "\n".join(lines)

async def answer_training_followup(
    *,
    message: str,
    owner_user_id: str,
    conversation_store: Any,
    thread_id: str,
) -> str:
    # NEUROVEST_V110_OWNER_HISTORY_GUARD
    # Verify thread ownership before reading conversation history.
    authenticated_owner = str(owner_user_id or "").strip()

    if not authenticated_owner:
        raise PermissionError(
            "Authenticated training owner required."
        )

    thread = await conversation_store.require_thread(thread_id)

    actual_owner = str(
        getattr(thread, "user_id", "") or ""
    ).strip()

    if actual_owner != authenticated_owner:
        raise PermissionError(
            "Training conversation is not available."
        )

    history = await conversation_store.list_messages(
        thread_id,
        limit=100,
        oldest_first=False,
    )

    # The store returns newest first.
    run_id = choose_run_id(
        message,
        list(reversed(history)),
    )

    if not run_id:
        return (
            "I couldn't identify a training run in this "
            "conversation. Please provide a training run ID."
        )

    evidence = get_authenticated_owner_training_result(
        owner_user_id=owner_user_id,
        run_id=run_id,
    )

    if not evidence:
        return (
            "That training run is not available to your "
            "authenticated account."
        )

    return explain_training(evidence, message)
