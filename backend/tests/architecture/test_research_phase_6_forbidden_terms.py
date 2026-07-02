from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STACK = ROOT / "app" / "stacks" / "research"

FORBIDDEN_TERMS = [
    "import yfinance",
    "import finnhub",
    "requests.get",
    "httpx.get",
    "calculate_rsi",
    "calculate_macd",
    "run_backtest",
    "generate_signal",
    "submit_order",
    "place_order",
    "execute_trade",
]


def test_research_phase_6_has_no_calculation_or_trading_logic() -> None:
    scanned = []

    for path in STACK.rglob("*.py"):
        text = path.read_text(errors="ignore")
        scanned.append(path)

        for term in FORBIDDEN_TERMS:
            assert term not in text, f"Forbidden research implementation term {term!r} found in {path}"

    assert scanned
