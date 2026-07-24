from backend.app.stacks.db_runtime.transaction_guard import transaction_guard
import yfinance as yf
from datetime import datetime
from backend.app.stacks.db_model.market_schema import StockHistory, StockLive
from backend.app.stacks.journal_ledger.ledger import async_session


# =========================
# FULL HISTORICAL LOAD
# =========================

async def load_full_history(symbol: str):

    ticker = yf.Ticker(symbol)

    df = ticker.history(period="max")  # pulls EVERYTHING available

    async with async_session() as session:

        async with transaction_guard(session):
            for idx, row in df.iterrows():

                record = StockHistory(
                    symbol=symbol,
                    timestamp=idx.to_pydatetime(),
                    open=row["Open"],
                    high=row["High"],
                    low=row["Low"],
                    close=row["Close"],
                    volume=row["Volume"],
                )

                session.add(record)

            await session.commit()


# =========================
# LIVE PRICE UPDATE LOOP
# =========================

async def update_live_price(symbol: str):

    ticker = yf.Ticker(symbol)
    price = ticker.fast_info["lastPrice"]

    async with async_session() as session:

        async with transaction_guard(session):
            record = StockLive(
                symbol=symbol,
                price=price,
                volume=0,
                updated_at=datetime.utcnow(),
            )

            await session.merge(record)
            await session.commit()
