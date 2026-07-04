from fastapi import FastAPI
from stacks.strategy.engine import generate_strategy_decision
from stacks.execution.paper_broker import process_portfolio_output

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # Startup logic here

@app.get("/api/v1/dashboard/summary")
def summary():
    symbol = "AAPL"  # Example symbol
    decision = generate_strategy_decision(symbol)
    
    if 'signal' in decision and 'symbol' in decision:
        process_portfolio_output(decision)  # Process the portfolio output
    
    return {"decision": decision}
