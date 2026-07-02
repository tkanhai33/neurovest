from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STACK = ROOT / "app" / "stacks" / "strategy"

FORBIDDEN_TERMS = [
    "generate_signal",
    "score_candidate",
    "optimize_strategy",
    "risk_approved",
    "submit_order",
    "place_order",
    "execute_trade",
    "paper_trade",
    "broker_client",
]


def test_strategy_phase_7_has_no_strategy_or_execution_logic() -> None:
    scanned = []

    for path in STACK.rglob("*.py"):
        text = path.read_text(errors="ignore")
        scanned.append(path)

        for term in FORBIDDEN_TERMS:
            assert term not in text, f"Forbidden strategy implementation term {term!r} found in {path}"

    assert scanned
