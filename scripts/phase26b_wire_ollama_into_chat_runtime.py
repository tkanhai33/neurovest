#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()
CHAT_DIR = ROOT / "backend/app/stacks/chat_public"

(CHAT_DIR / "chat_runtime.py").write_text(r'''from backend.app.stacks.chat_public.chat_intent_regex import detect_chat_intent
from backend.app.stacks.chat_public.ollama_chat_client import ask_ollama


def handle_chat_message(message: str):
    intent = detect_chat_intent(message)

    if intent.blocked:
      return {
          "status": "blocked",
          "response": {
              "type": "text",
              "message": "Live execution is locked. I can discuss the plan, risk, and simulation, but I cannot place real trades from chat.",
          },
          "intent": intent.intent,
      }

    if intent.intent == "graph_reset":
        return {"status": "ok", "response": {"type": "direct_command", "command": "graph_reset"}}

    if intent.intent == "graph_validate":
        return {"status": "ok", "response": {"type": "direct_command", "command": "graph_validate"}}

    if intent.intent == "simulate_trade":
        return {
            "status": "ok",
            "response": {
                "type": "direct_command",
                "command": "simulate_trade",
                "symbol": intent.symbol,
            },
        }

    try:
        reply = ask_ollama(
            message,
            intent=intent.intent,
            symbol=intent.symbol,
        )
    except Exception as e:
        reply = f"Neuro local model is unavailable: {type(e).__name__}: {e}"

    return {
        "status": "ok",
        "response": {
            "type": "text",
            "message": reply,
        },
        "intent": intent.intent,
        "symbol": intent.symbol,
    }
''')

print("patched Phase 26B Ollama into chat runtime")
