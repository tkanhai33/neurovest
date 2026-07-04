from spine.L5_api.neuro_state import STATE


APPROVAL_TRIGGERS = {"approve", "confirm", "yes", "run it", "execute"}


def should_execute(user_input: str) -> bool:
    return user_input.strip().lower() in APPROVAL_TRIGGERS


def process_message(user_input: str, plan_fn, execute_fn=None):
    """
    ChatGPT-style control loop:

    1. Always PLAN first
    2. Wait for approval
    3. Execute ONLY on explicit approval
    """

    # -------------------------
    # APPROVAL PATH
    # -------------------------
    if should_execute(user_input):
        if STATE.last_action and execute_fn:
            result = execute_fn(STATE.last_action)
            STATE.awaiting_approval = False
            return {
                "mode": "EXECUTED",
                "result": result,
                "note": "action executed from last approved plan"
            }

        return {
            "mode": "NO_PENDING_ACTION",
            "note": "nothing to execute"
        }

    # -------------------------
    # PLANNING PATH
    # -------------------------
    plan = plan_fn(user_input)

    STATE.last_plan = plan
    STATE.last_action = plan.get("next_action") if isinstance(plan, dict) else None
    STATE.awaiting_approval = True

    return {
        "mode": "PLANNED",
        "plan": plan,
        "awaiting_approval": True
    }
