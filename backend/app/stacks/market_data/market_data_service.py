from backend.app.stacks.market_data.feed import get_live_price_quote


async def get_live_market_price_for_api(symbol: str):
    return await get_live_price_quote(symbol)
