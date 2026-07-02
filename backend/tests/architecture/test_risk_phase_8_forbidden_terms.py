from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STACK = ROOT / "app" / "stacks" / "risk"

FORBIDDEN_TERMS = [
    "calculate_position_size",
    "calculate_drawdown",
    "calculate_exposure",
    "approve_trade",
    "submit_order",
    "place_order",
    "execute_trade",
    "paper_trade",
    "broker_client",
]


def test_risk_phase_8_has_no_risk_or_execution_logic() -> None:
    scanned = []

    for path in STACK.rglob("*.py"):
        text = path.read_text(errors="ignore")
        scanned.append(path)

        for term in FORBIDDEN_TERMS:
            assert term not in text, f"Forbidden risk implementation term {term!r} found in {path}"

    assert scanned
