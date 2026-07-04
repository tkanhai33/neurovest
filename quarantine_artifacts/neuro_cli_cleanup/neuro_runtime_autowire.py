from __future__ import annotations

import inspect
from spine.L5_api.repo_reasoning_layer import reason_and_plan
from spine.L5_api.repo_autonomous_orchestrator import orchestrator
from spine.L5_api.neuro_state import STATE


def patched_chat(message: str) -> dict:
    """
    Drop-in replacement ChatGPT-style controller.
    """

    # 1. ALWAYS GENERATE PLAN FIRST
    plan = reason_and_plan(message)

    STATE.last_plan = plan
    STATE.last_action = plan.get("system_output", {}).get("next_steps", [{}])[0]
    STATE.awaiting_approval = True

    return {
        "mode": "PLANNED",
        "response": plan,
        "next_action": STATE.last_action,
        "awaiting_approval": True
    }


def patched_execute(message: str) -> dict:
    """
    Only runs when user explicitly approves.
    """

    if not STATE.last_action:
        return {
            "mode": "NO_ACTION",
            "message": "Nothing pending to execute"
        }

    result = orchestrator.step(message)

    STATE.awaiting_approval = False

    return {
        "mode": "EXECUTED",
        "result": result
    }


def chat(message: str) -> dict:
    """
    SINGLE ENTRYPOINT — replaces everything.
    """

    msg = message.strip().lower()

    if msg in ["approve", "confirm", "yes", "run it", "execute"]:
        return patched_execute(message)

    return patched_chat(message)
