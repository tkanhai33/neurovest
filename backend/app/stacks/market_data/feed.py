"""DOMAIN_LOGIC_V1 live yfinance market data feed harvester."""
import asyncio
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor

# Dedicated thread pool executor to keep yfinance network blockages non-blocking
_executor = ThreadPoolExecutor(max_workers=3)

def _fetch_yf_snapshot(symbol: str) -> dict:
    """Synchronous worker that pulls real live asset data maps from the yfinance engine."""
    try:
        ticker = yf.Ticker(symbol)
        # Fast query of the most recent 1-day intraday data tracking grid
        fast_info = ticker.fast_info

        current_price = fast_info.get("last_price")
        prev_close = fast_info.get("previous_close")

        # If fast_info yields empty fields, pull from standard history matrices safely
        if current_price is None:
            hist = ticker.history(period="1d", interval="1m")
            if not hist.empty:
                current_price = float(hist["Close"].iloc[-1])
                prev_close = float(hist["Close"].iloc[0])
            else:
                raise ValueError("Empty ticker asset price dataframe returned.")

        return {
            "status": "ok",
            "symbol": symbol,
            "price": float(current_price),
            "previous_close": float(prev_close) if prev_close else float(current_price)
        }
    except Exception as e:
        return {
            "status": "error",
            "symbol": symbol,
            "price": None,
            "previous_close": None,
            "provider": "yfinance",
            "error": f"{type(e).__name__}: {e}",
        }

async def get_live_market_price(symbol: str) -> dict:
    """Asynchronously extracts live financial metrics via yfinance."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _fetch_yf_snapshot, symbol)


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
        previous_close = quote.get("previous_close")

        return {
            "status": "ok" if price is not None else "error",
            "symbol": symbol,
            "price": price,
            "previous_close": previous_close,
            "provider": quote.get("provider", "yfinance"),
            "timestamp": quote.get("timestamp"),
            "error": quote.get("error"),
        }

    except Exception as e:
        return {
            "status": "error",
            "symbol": symbol,
            "price": None,
            "provider": "yfinance",
            "error": f"{type(e).__name__}: {e}",
        }
