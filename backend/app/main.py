from fastapi import FastAPI, Depends
from stacks.strategy.engine import generate_strategy_decision
from stacks.execution.paper_broker import process_portfolio_output

app = FastAPI()

async def init_strategy_engine():
    # Initialize strategy engine logic here
    pass

async def init_paper_broker():
    # Initialize paper broker logic here
    pass

@app.on_event("startup")
async def startup_event():
    await init_strategy_engine()
    await init_paper_broker()

@app.get("/api/v1/dashboard/summary")
def summary(strategy_engine=Depends(init_strategy_engine), paper_broker=Depends(init_paper_broker)):
    symbol = "AAPL"  # Example symbol
    decision = generate_strategy_decision(symbol)
    
    if 'signal' in decision and 'symbol' in decision:
        process_portfolio_output(decision)  # Process the portfolio output
    
    return {"decision": decision}
