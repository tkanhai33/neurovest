#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()
CHAT_DIR = ROOT / "backend/app/stacks/chat_public"
CHAT_DIR.mkdir(parents=True, exist_ok=True)

(CHAT_DIR / "chat_intent_regex.py").write_text(r'''import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ChatIntent:
    intent: str
    symbol: str | None = None
    blocked: bool = False


COMMAND_PATTERNS = {
    "graph_reset": re.compile(r"^\s*(graph[_\s-]?reset)\s*$", re.I),
    "graph_validate": re.compile(r"^\s*(graph[_\s-]?validate)\s*$", re.I),
    "simulate_trade": re.compile(r"^\s*(simulate[_\s-]?trade)\s+([A-Z][A-Z0-9.\-]{0,12})\s*$", re.I),
}

BLOCKED_PATTERNS = [
    re.compile(r"\b(place|send|execute|submit)\b.*\b(live|real)\b.*\b(order|trade|buy|sell)\b", re.I),
    re.compile(r"\b(turn on|enable)\b.*\b(live trading|broker execution|real orders)\b", re.I),
]

TRADING_PATTERNS = [
    re.compile(r"\b(should i|do we|would you)\b.*\b(buy|sell|hold|trade)\b", re.I),
    re.compile(r"\b(price|market|strategy|risk|portfolio|position|stock|ticker)\b", re.I),
    re.compile(r"\b([A-Z]{1,5}(\.TO)?)\b"),
]


def detect_chat_intent(message: str) -> ChatIntent:
    clean = message.strip()

    for pattern in BLOCKED_PATTERNS:
        if pattern.search(clean):
            return ChatIntent(intent="blocked_live_execution", blocked=True)

    for intent, pattern in COMMAND_PATTERNS.items():
        match = pattern.search(clean)
        if match:
            symbol = match.group(2).upper() if intent == "simulate_trade" and match.lastindex and match.lastindex >= 2 else None
            return ChatIntent(intent=intent, symbol=symbol)

    for pattern in TRADING_PATTERNS:
        if pattern.search(clean):
            symbol_match = re.search(r"\b([A-Z]{1,5}(?:\.TO)?)\b", clean)
            return ChatIntent(
                intent="trading_conversation",
                symbol=symbol_match.group(1).upper() if symbol_match else None,
            )

    return ChatIntent(intent="general_conversation")
''')

(CHAT_DIR / "ollama_chat_client.py").write_text(r'''import json
import urllib.request


OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
DEFAULT_MODEL = "llama3.1"


def ask_ollama(message: str, *, intent: str = "general_conversation", symbol: str | None = None) -> str:
    system = (
        "You are Neuro, the user's trading system assistant. "
        "Be clear, practical, and concise. "
        "Do not claim live orders were placed. "
        "If asked for live execution, say execution is locked unless explicitly certified."
    )

    if intent == "trading_conversation":
        system += " You may discuss market logic, strategy, risk, portfolio, and symbol context, but do not provide financial guarantees."

    payload = {
        "model": DEFAULT_MODEL,
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

    with urllib.request.urlopen(req, timeout=20) as response:
        data = json.loads(response.read().decode("utf-8"))

    return data.get("message", {}).get("content", "").strip() or "Neuro online."
''')

print("patched Phase 26A chat intent regex + Ollama client")
