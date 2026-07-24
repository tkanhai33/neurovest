import datetime

from sqlalchemy import ForeignKey, UniqueConstraint, func, select
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.stacks.db_runtime.database import (
    Base,
    async_session,
)

class OrderHistory(Base):
    __tablename__ = "order_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(
        ForeignKey(
            "identity_users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    symbol: Mapped[str] = mapped_column(nullable=False)
    signal: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)
    timestamp: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow)
    allocated_capital: Mapped[float] = mapped_column(nullable=True)
    slippage_price: Mapped[float] = mapped_column(nullable=True)
    commission_paid: Mapped[float] = mapped_column(nullable=True)

class PortfolioInventory(Base):
    __tablename__ = "portfolio_inventory"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "symbol",
            name="uq_portfolio_inventory_user_id_symbol",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(
        ForeignKey(
            "identity_users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    symbol: Mapped[str] = mapped_column(nullable=False)
    shares_quantity: Mapped[float] = mapped_column(default=0.0)
    average_entry_price: Mapped[float] = mapped_column(default=0.0)
    total_cost_basis: Mapped[float] = mapped_column(default=0.0)
    realized_pnl: Mapped[float] = mapped_column(default=0.0)
    last_updated: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

async def save_log(
    trade_result: dict,
    *,
    user_id: str,
    trace_id: str | None = None,
):
    normalized_user_id = str(
        user_id
    ).strip()

    if not normalized_user_id:
        raise ValueError(
            "Ledger ownership user_id cannot be empty"
        )

    if not trade_result:
        return

    symbol = trade_result.get("symbol", "UNKNOWN")
    status = trade_result.get("status", "UNKNOWN")

    raw_signal = trade_result.get("signal", "UNKNOWN")
    signal_str = raw_signal.get("action", "UNKNOWN") if isinstance(raw_signal, dict) else str(raw_signal)

    allocated_capital = trade_result.get("allocated_capital")
    slippage_price = trade_result.get("slippage_price")
    commission_paid = trade_result.get("commission_paid")

    async with async_session() as session:
        async with session.begin():
            new_order = OrderHistory(
                user_id=normalized_user_id,
                symbol=symbol,
                signal=signal_str,
                status=status,
                allocated_capital=allocated_capital,
                slippage_price=slippage_price,
                commission_paid=commission_paid,
            )
            session.add(new_order)

            if status == "executed" and allocated_capital and slippage_price:
                stmt = select(
                    PortfolioInventory
                ).where(
                    PortfolioInventory.user_id
                    == normalized_user_id,
                    PortfolioInventory.symbol
                    == symbol,
                )
                res = await session.execute(stmt)
                position = res.scalar()

                shares_filled = float(allocated_capital) / float(slippage_price)

                if not position:
                    position = PortfolioInventory(
                        user_id=normalized_user_id,
                        symbol=symbol,
                        shares_quantity=shares_filled,
                        average_entry_price=float(
                            slippage_price
                        ),
                        total_cost_basis=float(
                            allocated_capital
                        ),
                    )
                    session.add(position)
                else:
                    if signal_str.lower() in ["buy", "long"]:
                        new_total_capital = float(position.total_cost_basis) + float(allocated_capital)
                        new_total_shares = float(position.shares_quantity) + shares_filled
                        position.shares_quantity = new_total_shares
                        position.total_cost_basis = new_total_capital
                        position.average_entry_price = new_total_capital / new_total_shares
                    elif signal_str.lower() in ["sell", "short"]:
                        # Calculate profit differences based on entry pricing vs current slippage fill prices
                        pnl_delta = shares_filled * (float(slippage_price) - float(position.average_entry_price))
                        position.realized_pnl = float(position.realized_pnl) + pnl_delta

                        position.shares_quantity = max(0.0, float(position.shares_quantity) - shares_filled)
                        position.total_cost_basis = float(position.shares_quantity) * float(position.average_entry_price)

            # Explicit flush forces SQLAlchemy to commit state updates directly to columns rows immediately
            await session.flush()
    if trace_id:
        from backend.app.core.runtime_trace import emit_runtime_step

        await emit_runtime_step(
            trace_id=trace_id,
            event_type="LEDGER_WRITE_COMPLETE",
            node="journal_ledger",
            source="execution",
            destination="journal_ledger",
            status="completed",
            symbol=symbol,
            message="Order history and portfolio inventory transaction committed",
            layer="L2",
            stack="journal_ledger",
            details={
                "signal": signal_str,
                "trade_status": status,
                "ownership_scope":
                    "authenticated_account",
            },
        )

        await emit_runtime_step(
            trace_id=trace_id,
            event_type="PORTFOLIO_INVENTORY_UPDATED",
            node="portfolio_accounting",
            source="journal_ledger",
            destination="portfolio_accounting",
            status="completed",
            symbol=symbol,
            message="Portfolio inventory update completed",
            layer="L2",
            stack="portfolio",
        )

    print(f"Database Log & Inventory Saved: {symbol} - {signal_str} - {status}")

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


async def read_max_allocated_capital(
    *,
    user_id: str,
) -> float | None:
    normalized_user_id = (
        _normalize_portfolio_read_user_id(
            user_id
        )
    )

    """
    Return the highest allocated capital through a
    journal-ledger-owned read-only query boundary.

    Consumers receive only a scalar value. Database
    sessions, ORM models, transactions, and mutation
    capabilities remain internal to journal_ledger.
    """

    async with async_session() as session:
        result = await session.execute(
            select(
                    func.max(
                        OrderHistory.allocated_capital
                    )
                ).where(
                    OrderHistory.user_id
                    == normalized_user_id
                )
        )

        value = result.scalar_one_or_none()

    if value is None:
        return None

    return float(value)
