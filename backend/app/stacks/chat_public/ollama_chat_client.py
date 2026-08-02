import os
import json
import urllib.request

from backend.app.stacks.chat_public.chat_system_prompt import SYSTEM_PROMPT
from backend.app.stacks.chat_public.time_context import get_chat_time_context


OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
DEFAULT_MODEL = "llama3.1:latest"

OLLAMA_TIMEOUT_SECONDS = float(
    os.getenv(
        "NEUROVEST_OLLAMA_TIMEOUT_SECONDS",
        "180",
    )
)


RUNTIME_MODEL_ALIASES = {
    "neuro-fast-no-think:latest": os.getenv(
        "NEUROVEST_FAST_RUNTIME_MODEL",
        "llama3.1:latest",
    ),
    "neuro-reason:latest": os.getenv(
        "NEUROVEST_REASON_RUNTIME_MODEL",
        "llama3.1:latest",
    ),
}


def resolve_runtime_model(
    requested_model: str | None,
) -> str | None:
    if requested_model is None:
        return None

    return RUNTIME_MODEL_ALIASES.get(
        requested_model,
        requested_model,
    )


def ask_ollama(
    message: str,
    *,
    intent: str = "general_conversation",
    symbol: str | None = None,
    model: str | None = None,
) -> str:
    system = SYSTEM_PROMPT + "\n\n" + get_chat_time_context()

    if intent == "trading_conversation":
        system += "\nYou may discuss market logic, strategy, risk, portfolio, and symbol context, but do not provide financial guarantees."

    payload = {
        "model": resolve_runtime_model(
            model
        ),
        "think": False,
        "stream": False,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": f"intent={intent}; symbol={symbol}; message={message}"},
        ],
    }

    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT_SECONDS) as response:
        data = json.loads(response.read().decode("utf-8"))

    return data.get("message", {}).get("content", "").strip() or "Neuro online."
