"""DOMAIN_LOGIC_V1 fallback for risk."""

from sqlalchemy.ext.asyncio import AsyncSession
from stacks.journal_ledger.ledger import async_session, OrderHistory

high_water_mark = 0.0

async def healthcheck(current_balance: float) -> dict:
    global high_water_mark
    
    # Open a database session context and query the historical log table to fetch the maximum equity value ever recorded (the High-Water Mark)
    async with async_session() as session:
        async with session.begin():
            max_equity_query = await session.execute(
                OrderHistory.select().order_by(OrderHistory.equity.desc()).limit(1)
            )
            max_equity_record = max_equity_query.scalar_one_or_none()
            
            if max_equity_record:
                high_water_mark = max_equity_record.equity
    
    # Calculate the real trailing drawdown drop
    drawdown = (high_water_mark - current_balance) / high_water_mark
    
    # If drawdown > 0.05 (exceeding our 5% safety ceiling risk constraint), return {"status": "unhealthy", "reason": "Trailing drawdown breach"}
    if drawdown > 0.05:
        return {"status": "unhealthy", "reason": "Trailing drawdown breach"}
    
    return {"status": "ok"}
