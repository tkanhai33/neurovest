from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import select
from stacks.journal_ledger.ledger import init_db, async_session, OrderHistory
from stacks.strategy.engine import generate_strategy_decision
from stacks.execution.paper_broker import process_portfolio_output

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initializes tables in your running PostgreSQL container on startup
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/api/v1/dashboard/summary")
async def summary():
    symbol = "AAPL"
    decision = generate_strategy_decision(symbol)
    
    if decision and decision.get("status") == "rebalanced":
        mock_matrix = [{'symbol': symbol, 'signal': 'buy'}]
        await process_portfolio_output(mock_matrix, decision)
        return {"status": "processed", "execution": "sent_to_broker", "decision": decision}
        
    return {"status": "no_action", "decision": decision}

@app.get("/api/v1/orders")
async def get_orders():
    """Queries and returns all historical transactions straight from the database."""
    async with async_session() as session:
        # Use modern SQLAlchemy 2.0 select syntax
        result = await session.execute(select(OrderHistory).order_by(OrderHistory.id.desc()))
        orders = result.scalars().all()
        
        # Format database objects into a clean JSON list layout
        order_list = [
            {
                "id": order.id,
                "symbol": order.symbol,
                "signal": order.signal,
                "status": order.status,
                "timestamp": order.timestamp.isoformat() if order.timestamp else None
            }
            for order in orders
        ]
        return {"total_records": len(order_list), "orders": order_list}

@app.get("/api/v1/analytics")
async def analytics():
    """Calculates basic processing statistics from the OrderHistory table."""
    async with async_session() as session:
        # Use modern SQLAlchemy 2.0 select syntax
        result = await session.execute(select(OrderHistory))
        orders = result.scalars().all()

        total_trades = len(orders)
        buy_count = sum(1 for order in orders if order.signal == "buy")
        sell_count = sum(1 for order in orders if order.signal == "sell")

        blocked_trades = sum(1 for order in orders if order.status != "executed")
        executed_trades = total_trades - blocked_trades

        blocked_percentage = (blocked_trades / total_trades) * 100 if total_trades > 0 else 0
        executed_percentage = (executed_trades / total_trades) * 100 if total_trades > 0 else 0

        return {
            "total_trades": total_trades,
            "buy_count": buy_count,
            "sell_count": sell_count,
            "blocked_percentage": blocked_percentage,
            "executed_percentage": executed_percentage
        }
