from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STACK = ROOT / "app" / "stacks" / "paper_trading"

FORBIDDEN_TERMS = [
    "simulate_fill",
    "match_order",
    "calculate_pnl",
    "update_position",
    "submit_order",
    "place_order",
    "execute_trade",
    "broker_client",
    "risk_approved",
    "strategy_signal",
]


def test_paper_trading_phase_9_has_no_execution_or_integration_logic() -> None:
    scanned = []

    for path in STACK.rglob("*.py"):
        text = path.read_text(errors="ignore")
        scanned.append(path)

        for term in FORBIDDEN_TERMS:
            assert term not in text, f"Forbidden paper trading implementation term {term!r} found in {path}"

    assert scanned
