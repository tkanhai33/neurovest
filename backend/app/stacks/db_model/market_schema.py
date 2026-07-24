from sqlalchemy import Column, String, Float, Integer, DateTime, JSON
from sqlalchemy.orm import declarative_base
import datetime

Base = declarative_base()


# =========================
# LIVE MARKET TABLE
# =========================
class StockLive(Base):
    __tablename__ = "stock_live"

    symbol = Column(String, primary_key=True)
    price = Column(Float)
    volume = Column(Float)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)


# =========================
# HISTORICAL SANDBOX TABLE
# =========================
class StockHistory(Base):
    __tablename__ = "stock_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String)
    timestamp = Column(DateTime)

    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)


# =========================
# RESEARCH TABLE (STRUCTURED)
# =========================
class ResearchData(Base):
    __tablename__ = "research_data"

    id = Column(Integer, primary_key=True, autoincrement=True)

    category = Column(String)   # algebra, calculus, stats, finance, etc
    title = Column(String)

    content = Column(JSON)      # formula + explanation structured

    tags = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
