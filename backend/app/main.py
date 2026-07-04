from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Neurovest API")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/api/v1/health")
def health(): return {"status": "healthy"}

@app.get("/api/v1/dashboard/summary")
def summary():
    return {
        "total_balance": 14250.75,
        "active_investments": 8300.00,
        "recent_transactions": [
            {"id": "tx_001", "description": "AI Compute", "amount": -45.00, "type": "debit", "date": "2026-07-01"},
            {"id": "tx_002", "description": "Dividend Payout", "amount": 125.50, "type": "credit", "date": "2026-06-30"}
        ]
    }
