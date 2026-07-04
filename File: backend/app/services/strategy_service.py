from pydantic import BaseModel

class StrategyService:
    async def generate_signal(self, symbol: str) -> dict:
        return {"symbol": symbol, "signal": "buy", "confidence": 0.95, "reason": "High momentum"}

    async def execute_trade(self, signal: dict) -> dict:
        # Simulate trade execution
        return {"message": f"Trade executed for {signal['symbol']} with action {signal['signal']}"}
