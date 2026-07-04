
import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"

def reason_about_repo(repo_snapshot: dict) -> dict:
    prompt = f'''
You are a system router.

Return ONLY JSON:

{
  "intent": "status|report|analyze|plan|unknown",
  "confidence": 0-1
}

Rules:
- status/report → system state
- analyze → architecture reasoning
- plan → improvement suggestions

DATA:
{json.dumps(repo_snapshot, indent=2)[:6000]}
'''

    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=10
        )

        raw = r.json().get("response", "{}")

        try:
            return json.loads(raw)
        except Exception:
            return {"intent": "unknown", "confidence": 0.0}

    except Exception as e:
        return {"intent": "unknown", "confidence": 0.0}
