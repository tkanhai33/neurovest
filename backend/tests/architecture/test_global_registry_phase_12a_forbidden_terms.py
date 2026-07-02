from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "app" / "shared" / "contracts"

FORBIDDEN_TERMS = [
    "enable_live_trading",
    "enable_broker_orders",
    "enable_runtime_scheduler",
    "enable_ai_mutation",
    "submit_order",
    "place_order",
    "execute_trade",
    "runtime_loop",
    "mutate_strategy",
]


def test_global_registry_has_no_unlock_or_runtime_logic() -> None:
    scanned = []

    for path in REGISTRY.rglob("*.py"):
        text = path.read_text(errors="ignore")
        scanned.append(path)

        for term in FORBIDDEN_TERMS:
            assert term not in text, f"Forbidden registry implementation term {term!r} found in {path}"

    assert scanned
