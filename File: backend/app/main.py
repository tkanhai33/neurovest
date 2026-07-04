from fastapi import FastAPI, Depends
from backend.app.config import settings
from backend.app.stacks.auth_identity.base import init as auth_init
from backend.app.stacks.chat_public.base import Chat_publicContract
from backend.app.stacks.db_model.base import Db_modelContract
from backend.app.stacks.execution.base import ExecutionContract
from backend.app.stacks.journal_ledger.base import Journal_ledgerContract
from backend.app.stacks.learning_research.base import Learning_researchContract
from backend.app.stacks.market_data.base import init as market_init, MarketDataService
from backend.app.stacks.notification.base import NotificationContract
from backend.app.stacks.portfolio.base import PortfolioContract
from backend.app.stacks.risk.base import RiskContract
from backend.app.stacks.snaptrade.base import SnaptradeContract
from backend.app.stacks.strategy.base import StrategyContract
from backend.app.stacks.wolfden_ai.base import Wolfden_aiContract

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    auth_init()
    market_init()
    # Initialize other stacks here

@app.get("/api/v1/health")
def health():
    return {
        "status": "healthy",
        "services": [
            {"name": Chat_publicContract.__name__, "status": "running"},
            {"name": Db_modelContract.__name__, "status": "running"},
            {"name": ExecutionContract.__name__, "status": "running"},
            {"name": Journal_ledgerContract.__name__, "status": "running"},
            {"name": Learning_researchContract.__name__, "status": "running"},
            {"name": NotificationContract.__name__, "status": "running"},
            {"name": PortfolioContract.__name__, "status": "running"},
            {"name": RiskContract.__name__, "status": "running"},
            {"name": SnaptradeContract.__name__, "status": "running"},
            {"name": StrategyContract.__name__, "status": "running"},
            {"name": Wolfden_aiContract.__name__, "status": "running"}
        ]
    }

@app.get("/api/v1/dashboard/summary")
def summary():
    # Implement dashboard summary logic here
    return {"message": "Dashboard summary data"}

# Register all stacks with the main application
market_data_service = MarketDataService()
