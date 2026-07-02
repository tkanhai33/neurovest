from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STACK = ROOT / "app" / "stacks" / "portfolio"

FORBIDDEN_TERMS = [
    "import snaptrade",
    "submit_order",
    "place_order",
    "execute_trade",
    "sync_broker_account",
    "broker_client",
    "calculate_performance",
    "mutate_portfolio",
]


def test_portfolio_phase_5_has_no_broker_or_mutation_logic() -> None:
    scanned = []

    for path in STACK.rglob("*.py"):
        text = path.read_text(errors="ignore")
        scanned.append(path)

        for term in FORBIDDEN_TERMS:
            assert term not in text, f"Forbidden portfolio implementation term {term!r} found in {path}"

    assert scanned
