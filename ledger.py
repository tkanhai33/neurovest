import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/neurovest"

# Modern SQLAlchemy 2.0 Base Class
class Base(DeclarativeBase):
    pass

class OrderHistory(Base):
    __tablename__ = "order_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(nullable=False)
    signal: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)
    timestamp: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow)
    allocated_capital: Mapped[float] = mapped_column(nullable=True)
    slippage_price: Mapped[float] = mapped_column(nullable=True)
    commission_paid: Mapped[float] = mapped_column(nullable=True)

# Explicit Asynchronous Engine Setup
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    """Exposed initialization endpoint called explicitly by the runtime main setup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def save_log(trade_result: dict):
    """Asynchronously records transaction payloads straight to the PostgreSQL server."""
    if not trade_result:
        return
    
    # Extract structural mapping safely
    symbol = trade_result.get("symbol", "UNKNOWN")
    status = trade_result.get("status", "UNKNOWN")
    
    # Handle both nested dictionaries or raw strings for signal keys safely
    raw_signal = trade_result.get("signal", "UNKNOWN")
    signal_str = raw_signal.get("action", "UNKNOWN") if isinstance(raw_signal, dict) else str(raw_signal)

    allocated_capital = trade_result.get("allocated_capital", None)
    slippage_price = trade_result.get("slippage_price", None)
    commission_paid = trade_result.get("commission_paid", None)

    async with async_session() as session:
        async with session.begin():
            new_order = OrderHistory(
                symbol=symbol,
                signal=signal_str,
                status=status,
                allocated_capital=allocated_capital,
                slippage_price=slippage_price,
                commission_paid=commission_paid
            )
            session.add(new_order)
    print(f"Database Log Saved: {symbol} - {signal_str} - {status}")
