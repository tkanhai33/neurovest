from __future__ import annotations

import math

from backend.app.core.runtime_trace import (
    create_trace_id,
    emit_runtime_step,
)
from backend.app.stacks.portfolio.accounting import (
    calculate_live_portfolio_equity,
)
from backend.app.stacks.risk.drawdown_guard import (
    healthcheck as drawdown_healthcheck,
)


async def get_risk_gate_for_api(
    symbol: str,
    *,
    owner_subject: str,
) -> dict:
    clean_symbol = (
        symbol.strip().upper()
        if isinstance(symbol, str)
        else ""
    )

    base = {
        "symbol": clean_symbol,
        "allowed": False,
        "gate": "risk",
        "provider": "risk_service",
    }

    if not clean_symbol:
        return {
            **base,
            "status": "error",
            "error": "missing_symbol",
        }

    if (
        not isinstance(owner_subject, str)
        or not owner_subject.strip()
    ):
        return {
            **base,
            "status": "error",
            "error": "missing_authenticated_owner",
        }

    try:
        trace_id = create_trace_id("risk-api")
        await emit_runtime_step(
            trace_id=trace_id,
            event_type="RISK_API_REQUEST_RECEIVED",
            node="risk_api",
            source="http_api",
            destination="risk_api",
            status="active",
            symbol=clean_symbol,
            message="Authenticated owner risk monitoring requested",
            layer="L5",
            stack="risk",
        )

        owner = owner_subject.strip()
        valuation = await calculate_live_portfolio_equity(
            user_id=owner,
        )
        cash = float(valuation["current_cash_balance"])

        if not math.isfinite(cash) or cash < 0:
            return {
                **base,
                "status": "blocked",
                "reason": "invalid_risk_balance",
            }

        monitor = await drawdown_healthcheck(
            cash,
            user_id=owner,
        )

        if (
            not isinstance(monitor, dict)
            or monitor.get("status") != "ok"
        ):
            return {
                **base,
                "status": "blocked",
                "reason": "risk_monitor_blocked",
                "drawdown_guard": monitor
                    if isinstance(monitor, dict) else None,
            }

        # Successful monitoring is NOT trade approval.
        # Equity drawdown and aggregate exposure policies
        # are not yet qualified as an integrated risk gate.
        return {
            **base,
            "status": "ok",
            "reason": "risk_policy_not_fully_qualified",
            "risk_monitor_available": True,
            "drawdown_guard": monitor,
        }

    except Exception:
        # Do not expose account or database error details.
        return {
            **base,
            "status": "error",
            "error": "risk_evaluation_unavailable",
        }
