from pydantic import BaseModel

class PortfolioService:
    async def allocate(self, portfolio_id: int, allocations: list[dict]) -> dict:
        # Simulate portfolio allocation
        return {"message": f"Portfolio {portfolio_id} allocated with allocations {allocations}"}
