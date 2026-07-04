"""DOMAIN_LOGIC_V1 journal ledger."""

import asyncio
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Initialize SQLAlchemy engine
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/neurovest"
engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()

# Declare the order_history table schema
class OrderHistory(Base):
    __tablename__ = 'order_history'
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    signal = Column(String, index=True)
    status = Column(String, index=True)
    timestamp = Column(DateTime, default=func.now())

# Create the table if it doesn't exist
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Refactor save_log to be an async function that commits to the database
async def save_log(trade_result: dict):
    # Simulate saving log logic
    async with sessionmaker(engine, expire_on_commit=False)() as session:
        order = OrderHistory(
            symbol=trade_result.get('symbol'),
            signal=trade_result.get('signal'),
            status=trade_result.get('status'),
            timestamp=func.now()
        )
        session.add(order)
        await session.commit()
        print(f"Log saved: {trade_result}")

# Initialize the database
asyncio.run(init_db())
