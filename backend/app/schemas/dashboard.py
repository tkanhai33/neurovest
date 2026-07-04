from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class TransactionBase(BaseModel):
    id: str = Field(..., description="Unique immutable financial transaction tracking ID")
    description: str = Field(..., description="Sanitized ledger description item")
    amount: float = Field(..., description="Transactional balance mutation delta value")
    type: str = Field(..., description="Transaction delta classification: credit or debit")
    date: str = Field(..., description="ISO timeline execution timestamp representation")

class DashboardSummarySchema(BaseModel):
    total_balance: float = Field(..., description="Aggregated cash ledger balance total sum")
    active_investments: float = Field(..., description="Aggregated actively tracked investment valuation")
    recent_transactions: List[TransactionBase] = Field(default=[], description="Auditable historical ledger list items")
