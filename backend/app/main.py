from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import select
from stacks.journal_ledger.ledger import init_db, async_session, OrderHistory
from stacks.strategy.engine import generate_strategy_decision
from stacks.execution.paper_broker import process_portfolio_output

@asynccontextmanager
async def lifespan(app: FastAPI):
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
    async with async_session() as session:
        result = await session.execute(select(OrderHistory).order_by(OrderHistory.id.desc()))
        orders = result.scalars().all()
        
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
async def get_analytics():
    """Queries order logs asynchronously and computes core portfolio performance matrices."""
    async with async_session() as session:
        result = await session.execute(select(OrderHistory))
        all_records = result.scalars().all()
        
        total_trades = len(all_records)
        buys = sum(1 for o in all_records if str(o.signal).lower() == 'buy' or str(o.signal).lower() == 'long')
        sells = sum(1 for o in all_records if str(o.signal).lower() == 'sell' or str(o.signal).lower() == 'short')
        blocked = sum(1 for o in all_records if o.status == 'blocked_by_risk')
        executed = sum(1 for o in all_records if o.status == 'executed')
        
        return {
            "total_trades_logged": total_trades,
            "buy_signals_count": buys,
            "sell_signals_count": sells,
            "risk_blocked_percentage": (blocked / total_trades * 100) if total_trades > 0 else 0.0,
            "execution_success_percentage": (executed / total_trades * 100) if total_trades > 0 else 0.0
        }
