"""DOMAIN_LOGIC_V1 system accounting and portfolio equity tracking engine."""
from sqlalchemy import select
from backend.app.stacks.journal_ledger.ledger import async_session, OrderHistory

STARTING_CAPITAL = 100000.00

def _normalize_portfolio_read_user_id(
    user_id: str,
) -> str:
    normalized_user_id = str(
        user_id
    ).strip()

    if not normalized_user_id:
        raise ValueError(
            "Authenticated portfolio user_id cannot be empty"
        )

    return normalized_user_id


async def calculate_live_portfolio_equity(
    *,
    user_id: str,
) -> dict:
    normalized_user_id = (
        _normalize_portfolio_read_user_id(
            user_id
        )
    )

    """Queries persistent database order history rows to compute real-time cash balances."""
    try:
        async with async_session() as session:
            result = await session.execute(select(
                OrderHistory
            ).where(
                OrderHistory.user_id
                == normalized_user_id
            ))
            records = result.scalars().all()

            current_cash = STARTING_CAPITAL
            total_commissions = 0.0

            # Reconstruct net capital balance dynamically from historical log rows
            for order in records:
                # Track fee deductions natively
                if order.commission_paid:
                    total_commissions += float(order.commission_paid)
                    current_cash -= float(order.commission_paid)

                # Update cash flows based on executed trade results
                if order.status == "executed" and order.allocated_capital:
                    if order.signal.lower() == "buy":
                        current_cash -= float(order.allocated_capital)
                    elif order.signal.lower() == "sell":
                        current_cash += float(order.allocated_capital)

            return {
                "starting_capital": STARTING_CAPITAL,
                "current_cash_balance": current_cash,
                "total_fees_paid": total_commissions,
                "net_liquidation_value": current_cash  # Expands when open position marking is added
            }
    except Exception as e:
        # Fallback to safe starting parameters if database cannot be reached
        return {
            "starting_capital": STARTING_CAPITAL,
            "current_cash_balance": STARTING_CAPITAL,
            "total_fees_paid": 0.0,
            "net_liquidation_value": STARTING_CAPITAL,
            "error": str(e)
        }
