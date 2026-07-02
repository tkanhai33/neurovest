from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STACK = ROOT / "app" / "stacks" / "ai_chat"

FORBIDDEN_TERMS = [
    "requests.post",
    "httpx.post",
    "ollama.chat",
    "ollama.generate",
    "model.generate",
    "execute_tool",
    "execute_trade",
    "submit_order",
    "place_order",
    "broker_client",
    "runtime_service",
    "financial_advice",
]


def test_ai_chat_phase_12_has_no_model_tool_or_execution_logic() -> None:
    scanned = []

    for path in STACK.rglob("*.py"):
        text = path.read_text(errors="ignore")
        scanned.append(path)

        for term in FORBIDDEN_TERMS:
            assert term not in text, f"Forbidden ai_chat implementation term {term!r} found in {path}"

    assert scanned
