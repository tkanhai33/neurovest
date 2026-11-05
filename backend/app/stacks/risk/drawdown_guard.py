from __future__ import annotations

import math

from backend.app.stacks.journal_ledger.ledger import (
    read_max_allocated_capital,
)


async def healthcheck(
    current_balance: float,
    *,
    user_id: str,
) -> dict:
    """
    Check that owner-scoped risk inputs are available.

    The legacy cash-based ratio is diagnostic only:
    it is NOT a verified portfolio-equity drawdown.
    No loss threshold is enforced until a validated
    equity-based risk policy is implemented.
    """
    if not isinstance(user_id, str) or not user_id.strip():
        return {
            "status": "blocked",
            "reason": "risk_owner_unavailable",
            "simulation_mode": True,
        }

    try:
        balance = float(current_balance)

        if not math.isfinite(balance) or balance < 0:
            return {
                "status": "blocked",
                "reason": "invalid_risk_balance",
                "simulation_mode": True,
            }

        user_id = user_id.strip()

        max_past_allocation = await read_max_allocated_capital(user_id=user_id)

        if max_past_allocation is None:
            reference = 100000.0
        else:
            allocation = float(max_past_allocation)
            if not math.isfinite(allocation) or allocation < 0:
                return {
                    "status": "blocked",
                    "reason": "invalid_risk_history",
                    "simulation_mode": True,
                }
            reference = max(allocation, 100000.0)

        high_water_mark = max(reference, balance)

        if not math.isfinite(high_water_mark) or high_water_mark <= 0:
            return {
                "status": "blocked",
                "reason": "invalid_risk_reference",
                "simulation_mode": True,
            }

        diagnostic_ratio = (
            high_water_mark - balance
        ) / high_water_mark

        return {
            "status": "ok",
            "trailing_drawdown": diagnostic_ratio,
            "drawdown_basis": "cash_only_diagnostic",
            "drawdown_limit_enforced": False,
            "simulation_mode": True,
        }

    except Exception as exc:
        # Do not silently approve an order when risk data fails.
        print(
            "Risk Monitor Unavailable:",
            type(exc).__name__,
        )
        return {
            "status": "blocked",
            "reason": "risk_monitor_unavailable",
            "simulation_mode": True,
        }
