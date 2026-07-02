from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STACK = ROOT / "app" / "stacks" / "market_data"

FORBIDDEN_TERMS = [
    "import yfinance",
    "import finnhub",
    "requests.get",
    "httpx.get",
    "submit_order",
    "place_order",
    "execute_trade",
    "risk_approved",
    "strategy_score",
]


def test_market_data_phase_4_has_no_provider_or_trading_logic() -> None:
    scanned = []

    for path in STACK.rglob("*.py"):
        text = path.read_text(errors="ignore")
        scanned.append(path)

        for term in FORBIDDEN_TERMS:
            assert term not in text, f"Forbidden market data implementation term {term!r} found in {path}"

    assert scanned
