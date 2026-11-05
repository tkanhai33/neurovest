"""DOMAIN_LOGIC_V1 system accounting and portfolio equity tracking engine."""
from datetime import date, datetime
from decimal import Decimal
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



# Historical data exception, not a general HOLD execution policy.
# IDs 5–36 were independently reconciled on 2026-10-13.
# Their recorded capital never entered portfolio_inventory.
# Retain the original rows and fail closed for every other anomaly.
def _is_verified_legacy_executed_hold(order: object) -> bool:
    try:
        record_id = getattr(order, "id")
        if type(record_id) is not int or not 5 <= record_id <= 36:
            return False

        if str(getattr(order, "status")).strip().lower() != "executed":
            return False

        if str(getattr(order, "signal")).strip().lower() != "hold":
            return False

        symbol = str(getattr(order, "symbol")).strip().upper()
        if symbol not in {"AAPL", "NVDA", "RY.TO", "TSLA"}:
            return False

        timestamp = getattr(order, "timestamp")
        if not isinstance(timestamp, datetime):
            return False
        if not (
            date(2026, 7, 4)
            <= timestamp.date()
            <= date(2026, 7, 5)
        ):
            return False

        capital = Decimal(str(getattr(order, "allocated_capital")))
        fill = Decimal(str(getattr(order, "slippage_price")))
        fee = Decimal(str(getattr(order, "commission_paid")))

        return (
            capital.is_finite()
            and Decimal("7824") < capital < Decimal("7830")
            and fill.is_finite()
            and fill > 0
            and fee == Decimal("1")
        )
    except (AttributeError, TypeError, ValueError, ArithmeticError):
        return False


async def calculate_cash_in_session(
    *,
    session,
    user_id: str,
) -> dict:
    """
    Reconcile owner cash within the caller's database session.

    Intended for use inside the already locked paper-ledger
    transaction. Does not commit or authorize orders.

    Existing legacy executed/HOLD exceptions are preserved.
    """
    owner = _normalize_portfolio_read_user_id(user_id)

    if session is None or not callable(
        getattr(session, "execute", None)
    ):
        raise ValueError("Transaction session required")

    result = await session.execute(
        select(OrderHistory).where(
            OrderHistory.user_id == owner
        )
    )
    records = result.scalars().all()

    current_cash = Decimal(str(STARTING_CAPITAL))
    total_commissions = Decimal("0")
    executed_count = 0

    for order in records:
        if str(order.status).strip().lower() != "executed":
            continue

        signal = str(order.signal).strip().lower()

        if (
            signal == "hold"
            and _is_verified_legacy_executed_hold(order)
        ):
            continue

        if signal not in ("buy", "long", "sell", "short"):
            raise ValueError(
                "Unsupported executed cash-flow action"
            )

        capital = Decimal(str(order.allocated_capital))
        fee = Decimal(str(
            order.commission_paid
            if order.commission_paid is not None
            else 0
        ))

        if (
            not capital.is_finite()
            or not fee.is_finite()
            or capital <= 0
            or fee < 0
        ):
            raise ValueError(
                "Invalid executed trade cash-flow values"
            )

        if signal in ("buy", "long"):
            current_cash -= capital
        else:
            current_cash += capital

        current_cash -= fee
        total_commissions += fee
        executed_count += 1

    if not current_cash.is_finite():
        raise ValueError("Cash reconciliation is nonfinite")

    return {
        "user_id": owner,
        "starting_capital": str(
            Decimal(str(STARTING_CAPITAL))
        ),
        "current_cash_balance": str(current_cash),
        "total_fees_paid": str(total_commissions),
        "executed_trade_count": executed_count,
        "scope": "caller_database_session",
        "net_liquidation_value": None,
        "execution_authorized": False,
    }


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

            current_cash = Decimal(str(STARTING_CAPITAL))
            total_commissions = Decimal("0")

            for order in records:
                if str(order.status).lower() != "executed":
                    continue

                signal = str(order.signal).strip().lower()

                if signal == "hold" and _is_verified_legacy_executed_hold(order):
                    # Verified historical non-trades: no cash movement or fee.
                    continue

                if signal not in ("buy", "long", "sell", "short"):
                    raise ValueError("Unsupported executed cash-flow action")

                capital = Decimal(str(order.allocated_capital))
                fee = Decimal(str(
                    order.commission_paid
                    if order.commission_paid is not None
                    else 0
                ))

                if (
                    not capital.is_finite()
                    or not fee.is_finite()
                    or capital <= 0
                    or fee < 0
                ):
                    raise ValueError("Invalid executed trade cash-flow values")

                if signal in ("buy", "long"):
                    current_cash -= capital
                else:
                    current_cash += capital

                current_cash -= fee
                total_commissions += fee

            return {
                "starting_capital": STARTING_CAPITAL,
                "current_cash_balance": float(current_cash),
                "total_fees_paid": float(total_commissions),
                # No validated market marks for all open holdings.
                # Cash is available separately; total equity is unknown.
                "net_liquidation_value": None,
            }
    except Exception as e:
        # Financial state is unknown after a database failure.
        # Never report starting capital as verified buying power.
        raise RuntimeError(
            "Paper portfolio cash balance unavailable"
        ) from e
