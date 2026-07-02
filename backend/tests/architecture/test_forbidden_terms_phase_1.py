from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_PHASE_1_TERMS = [
    "submit_order",
    "place_order",
    "live_trade",
    "execute_trade",
    "autonomous_trading_loop",
]


def test_phase_1_contains_no_execution_terms() -> None:
    scanned = []

    for path in ROOT.rglob("*.py"):
        if ".venv" in path.parts:
            continue

        # Architecture tests may contain forbidden words inside their own guard lists.
        if "tests" in path.parts and "architecture" in path.parts:
            continue

        text = path.read_text(errors="ignore")
        scanned.append(path)

        for term in FORBIDDEN_PHASE_1_TERMS:
            assert (
                term not in text
            ), f"Forbidden Phase 1 term {term!r} found in {path}"

    assert scanned
