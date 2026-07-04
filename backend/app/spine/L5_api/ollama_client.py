
import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"


def ask_ollama(user_input: str) -> dict:
    prompt = f'''
You are an intent classifier.

Return ONLY JSON:
{{
  "intent": "status|report|unknown",
  "confidence": 0-1
}}

Input: {user_input}
'''

    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=5
        )

        raw = r.json().get("response", "{}")

        try:
            return json.loads(raw)
        except Exception:
            return {"intent": "unknown", "confidence": 0.0}

    except Exception:
        return {"intent": "unknown", "confidence": 0.0}
