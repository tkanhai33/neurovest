from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from stacks.journal_ledger.ledger import init_db, get_async_session, OrderHistory

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/api/v1/dashboard/summary")
async def summary():
    symbol = "AAPL"
    
    # Assuming generate_strategy_decision and process_portfolio_output are defined elsewhere
    decision = generate_strategy_decision(symbol)
    
    # If the portfolio manager has successfully rebalanced the assets,
    # cascade that matrix down to the paper broker to execute the simulated fill and save the logs
    if decision and decision.get("status") == "rebalanced":
        mock_matrix = [{'symbol': symbol, 'signal': 'buy'}]
        await process_portfolio_output(mock_matrix, decision)
        return {"status": "processed", "execution": "sent_to_broker", "decision": decision}
        
    return {"status": "no_action", "decision": decision}

@app.get("/api/v1/orders")
async def get_orders(session: AsyncSession = Depends(get_async_session)):
    query = select(OrderHistory).order_by(OrderHistory.timestamp.desc())
    result = await session.execute(query)
    orders = [dict(row._asdict()) for row in result.scalars()]
    return {"orders": orders}
