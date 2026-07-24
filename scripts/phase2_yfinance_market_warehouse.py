from pathlib import Path
import json
import sys
from datetime import datetime, UTC

import yfinance as yf

ROOT = Path(".").resolve()
WAREHOUSE = ROOT / "runtime" / "market_warehouse"
HISTORY_DIR = WAREHOUSE / "history"
LIVE_DIR = WAREHOUSE / "live"

REGISTRY = WAREHOUSE / "symbol_registry.json"

HISTORY_DIR.mkdir(parents=True, exist_ok=True)
LIVE_DIR.mkdir(parents=True, exist_ok=True)


def now():
    return datetime.now(UTC).isoformat()


def symbol_to_file(symbol: str) -> str:
    return symbol.replace(".", "_")


def load_registry():
    if not REGISTRY.exists():
        raise FileNotFoundError(f"Missing registry: {REGISTRY}")
    return json.loads(REGISTRY.read_text())


def save_registry(data):
    data["updated_at"] = now()
    REGISTRY.write_text(json.dumps(data, indent=2))


def fetch_history(symbol: str):
    out_csv = HISTORY_DIR / f"{symbol_to_file(symbol)}_history.csv"

    if out_csv.exists():
        print(f"⏭ History exists, skipping full backfill: {symbol}")
        return True

    print(f"📈 Fetching max history: {symbol}")
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="max", interval="1d", auto_adjust=False)

    if df.empty:
        print(f"⚠ No history returned: {symbol}")
        return False

    df.to_csv(out_csv)
    print(f"✔ History saved: {out_csv} rows={len(df)}")
    return True


def force_fetch_history(symbol: str):
    print(f"📈 FORCE fetching max history: {symbol}")
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="max", interval="1d", auto_adjust=False)

    if df.empty:
        print(f"⚠ No history returned: {symbol}")
        return False

    out_csv = HISTORY_DIR / f"{symbol_to_file(symbol)}_history.csv"
    df.to_csv(out_csv)

    print(f"✔ History overwritten: {out_csv} rows={len(df)}")
    return True


def fetch_live(symbol: str):
    print(f"🟢 Fetching live snapshot: {symbol}")

    ticker = yf.Ticker(symbol)

    try:
        fast = dict(ticker.fast_info)
    except Exception:
        fast = {}

    info = {
        "symbol": symbol,
        "source": "yfinance",
        "fetched_at": now(),
        "last_price": fast.get("last_price") or fast.get("lastPrice"),
        "currency": fast.get("currency"),
        "market_cap": fast.get("market_cap") or fast.get("marketCap"),
        "day_high": fast.get("day_high") or fast.get("dayHigh"),
        "day_low": fast.get("day_low") or fast.get("dayLow"),
        "previous_close": fast.get("previous_close") or fast.get("previousClose"),
    }

    out_json = LIVE_DIR / f"{symbol_to_file(symbol)}_live.json"
    out_json.write_text(json.dumps(info, indent=2, default=str))

    print(f"✔ Live saved: {out_json}")
    return True


def main():
    mode = "incremental"

    if len(sys.argv) > 1:
        mode = sys.argv[1].strip().lower()

    if mode not in {"incremental", "full"}:
        print("Usage:")
        print("  python3 scripts/phase2_yfinance_market_warehouse.py incremental")
        print("  python3 scripts/phase2_yfinance_market_warehouse.py full")
        raise SystemExit(2)

    print(f"🧠 PHASE 2D: YFINANCE MARKET WAREHOUSE mode={mode}")

    registry = load_registry()

    for item in registry.get("symbols", []):
        symbol = item["symbol"]

        if not item.get("enabled", True):
            continue

        try:
            if mode == "full":
                history_ok = force_fetch_history(symbol)
            else:
                history_ok = fetch_history(symbol)

            live_ok = fetch_live(symbol)

            item["history_status"] = "complete" if history_ok else "failed"
            item["live_status"] = "complete" if live_ok else "failed"
            item["last_sync_mode"] = mode
            item["last_sync_at"] = now()

            if "last_error" in item:
                del item["last_error"]

        except Exception as e:
            item["history_status"] = "failed"
            item["live_status"] = "failed"
            item["last_sync_mode"] = mode
            item["last_error"] = str(e)
            item["last_sync_at"] = now()
            print(f"❌ {symbol}: {e}")

    save_registry(registry)

    print("✔ Phase 2D yfinance warehouse sync complete")


if __name__ == "__main__":
    main()
