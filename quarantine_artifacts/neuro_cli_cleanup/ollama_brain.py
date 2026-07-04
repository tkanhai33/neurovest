from __future__ import annotations

import json
import requests


def ollama_reason(message: str, context: dict = None) -> dict:
    """
    Connects real LLM reasoning to your system.
    """

    prompt = f"""
You are the reasoning layer of a software build system.

User message:
{message}

System context:
{json.dumps(context or {}, indent=2)}

Return:
- intent (what user wants)
- action_hint (what system should do next)
- clarity_summary
"""

    r = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    return r.json()
