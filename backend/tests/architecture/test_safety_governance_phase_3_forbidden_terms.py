from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STACK = ROOT / "app" / "stacks" / "safety_governance"

FORBIDDEN_TERMS = [
    "enable_live_trading",
    "unlock_broker_orders",
    "set_live_mode",
    "place_order",
    "submit_order",
    "execute_trade",
    "enable_autonomous_runtime",
    "enable_ai_mutation",
]


def test_safety_governance_phase_3_has_no_unlock_implementation() -> None:
    scanned = []

    for path in STACK.rglob("*.py"):
        text = path.read_text(errors="ignore")
        scanned.append(path)

        for term in FORBIDDEN_TERMS:
            assert term not in text, f"Forbidden safety implementation term {term!r} found in {path}"

    assert scanned
