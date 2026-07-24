#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()

feed = ROOT / "backend/app/stacks/market_data/feed.py"
main = ROOT / "backend/app/main.py"

feed_text = feed.read_text()

feed_append = r'''

async def get_live_price_quote(symbol: str):
    symbol = symbol.strip().upper()

    if not symbol:
        return {
            "status": "error",
            "symbol": symbol,
            "price": None,
            "provider": "yfinance",
            "error": "missing_symbol",
        }

    try:
        quote = await get_live_market_price(symbol)
        price = quote.get("price")

        return {
            "status": "ok" if price is not None else "error",
            "symbol": symbol,
            "price": price,
            "provider": quote.get("provider", "yfinance"),
            "timestamp": quote.get("timestamp"),
            "raw": quote,
        }

    except Exception as e:
        return {
            "status": "error",
            "symbol": symbol,
            "price": None,
            "provider": "yfinance",
            "error": f"{type(e).__name__}: {e}",
        }
'''

if "def get_live_price_quote" not in feed_text:
    feed_text += feed_append

feed.write_text(feed_text)

main_text = main.read_text()

if "get_live_market_price_for_api" not in main_text:
    import_line = "from backend.app.stacks.market_data.market_data_service import get_live_market_price_for_api\n"

    if import_line not in main_text:
        main_text = import_line + main_text

route = r'''

@app.get("/api/v1/market/live-price/{symbol}")
async def api_live_market_price(symbol: str):
    return await get_live_market_price_for_api(symbol)
'''

if '"/api/v1/market/live-price/{symbol}"' not in main_text:
    main_text += route

main.write_text(main_text)

print("patched Phase 11 live market price API bridge")
