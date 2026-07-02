from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STACK = ROOT / "app" / "stacks" / "broker_integration"

FORBIDDEN_TERMS = [
    "import snaptrade",
    "SnapTrade",
    "requests.get",
    "requests.post",
    "httpx.get",
    "httpx.post",
    "access_token",
    "refresh_token",
    "submit_order",
    "place_order",
    "execute_trade",
    "live_trade",
]


def test_broker_integration_phase_10_has_no_broker_or_execution_logic() -> None:
    scanned = []

    for path in STACK.rglob("*.py"):
        text = path.read_text(errors="ignore")
        scanned.append(path)

        for term in FORBIDDEN_TERMS:
            assert term not in text, f"Forbidden broker implementation term {term!r} found in {path}"

    assert scanned
