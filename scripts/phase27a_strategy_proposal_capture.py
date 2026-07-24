#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()
CANDIDATE_DIR = ROOT / "runtime/strategy_candidates"
CHAT_DIR = ROOT / "backend/app/stacks/chat_public"

CANDIDATE_DIR.mkdir(parents=True, exist_ok=True)

(CHAT_DIR / "strategy_proposal_capture.py").write_text(r'''import json
import re
from datetime import datetime, UTC
from pathlib import Path
from uuid import uuid4

ROOT = Path(".").resolve()
OUT_DIR = ROOT / "runtime/strategy_candidates"
OUT_DIR.mkdir(parents=True, exist_ok=True)


STRATEGY_TERMS = [
    "strategy",
    "entry",
    "exit",
    "stop-loss",
    "stop loss",
    "take-profit",
    "take profit",
    "moving average",
    "rsi",
    "macd",
    "simulate",
    "backtest",
]


def looks_like_strategy_proposal(message: str) -> bool:
    clean = message.lower()
    return any(term in clean for term in STRATEGY_TERMS)


def extract_symbol(message: str) -> str | None:
    matches = re.findall(r"\b[A-Z]{2,5}(?:\.TO)?\b", message)
    return matches[0] if matches else None


def capture_strategy_proposal(user_message: str, assistant_message: str, intent: str | None = None, symbol: str | None = None):
    if not looks_like_strategy_proposal(user_message + "\n" + assistant_message):
        return None

    candidate_id = f"candidate_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}"
    resolved_symbol = symbol or extract_symbol(user_message) or extract_symbol(assistant_message)

    candidate = {
        "candidate_id": candidate_id,
        "created_at": datetime.now(UTC).isoformat(),
        "status": "captured_pending_review",
        "origin": "chat_ollama_proposal",
        "intent": intent,
        "symbol": resolved_symbol,
        "requires_user_approval": True,
        "requires_sandbox_test": True,
        "requires_promotion_review": True,
        "user_message": user_message,
        "assistant_proposal": assistant_message,
        "safety": {
            "live_execution_allowed": False,
            "broker_execution_allowed": False,
            "simulation_only": True,
        },
    }

    out = OUT_DIR / f"{candidate_id}.json"
    out.write_text(json.dumps(candidate, indent=2))

    return {
        "captured": True,
        "candidate_id": candidate_id,
        "path": str(out),
        "symbol": resolved_symbol,
        "status": "captured_pending_review",
    }
''')

# Patch chat runtime to capture assistant strategy proposals after Ollama response.
runtime = CHAT_DIR / "chat_runtime.py"
text = runtime.read_text()

if "strategy_proposal_capture" not in text:
    text = text.replace(
        "from backend.app.stacks.chat_public.ollama_chat_client import ask_ollama",
        "from backend.app.stacks.chat_public.ollama_chat_client import ask_ollama\nfrom backend.app.stacks.chat_public.strategy_proposal_capture import capture_strategy_proposal",
    )

if "strategy_capture = capture_strategy_proposal" not in text:
    text = text.replace(
'''    return {
        "status": "ok",
        "response": {
            "type": "text",
            "message": reply,
        },
        "intent": intent.intent,
        "symbol": intent.symbol,
    }''',
'''    strategy_capture = capture_strategy_proposal(
        str(message),
        reply,
        intent=intent.intent,
        symbol=intent.symbol,
    )

    return {
        "status": "ok",
        "response": {
            "type": "text",
            "message": reply,
        },
        "intent": intent.intent,
        "symbol": intent.symbol,
        "strategy_capture": strategy_capture,
    }'''
    )

runtime.write_text(text)
print("patched Phase 27A strategy proposal capture")
