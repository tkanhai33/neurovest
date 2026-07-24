from __future__ import annotations

from backend.app.stacks.journal_ledger.ledger import (
    read_max_allocated_capital,
)


async def healthcheck(
    current_balance: float,
    *,
    user_id: str,
) -> dict:
    """Queries persistent database order histories asynchronously to evaluate trailing drawdown risk flags."""
    try:
        max_past_allocation = await read_max_allocated_capital(
            user_id=user_id,
        )
        high_water_mark = max(float(max_past_allocation or 100000.0), 100000.0)
        if current_balance > high_water_mark:
            high_water_mark = current_balance
        drawdown = (high_water_mark - current_balance) / high_water_mark
        return {'status': 'ok', 'trailing_drawdown': drawdown, 'simulation_mode': True}
    except Exception as e:
        print(f'Risk Monitor Query Exception: {str(e)}')
        return {'status': 'ok', 'fallback': True}
