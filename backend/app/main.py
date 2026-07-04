from contextlib import asynccontextmanager
from fastapi import FastAPI
from stacks.journal_ledger.ledger import init_db
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
    
    # If the portfolio manager has successfully rebalanced the assets,
    # cascade that matrix down to the paper broker to execute the simulated fill and save the logs
    if decision and decision.get("status") == "rebalanced":
        mock_matrix = [{'symbol': symbol, 'signal': 'buy'}]
        await process_portfolio_output(mock_matrix, decision)
        return {"status": "processed", "execution": "sent_to_broker", "decision": decision}
        
    return {"status": "no_action", "decision": decision}
