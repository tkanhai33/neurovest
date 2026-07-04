import json
import subprocess
from typing import Dict, Any


class OllamaStrategyEngine:
    """
    FIRST REAL INTELLIGENCE MODULE (LOCAL LLM)

    Uses Ollama to generate trading decisions.
    """

    def __init__(self, model: str = "llama3.1"):
        self.model = model

    # -----------------------------
    # PUBLIC ENTRYPOINT
    # -----------------------------

    def generate_signal(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self._build_prompt(market_data)

        raw = self._query_ollama(prompt)

        return self._parse_response(raw)

    # -----------------------------
    # PROMPT BUILDER
    # -----------------------------

    def _build_prompt(self, data: Dict[str, Any]) -> str:
        return f"""
You are a strict trading signal engine.

Return ONLY valid JSON.

Schema:
{{
  "action": "buy | sell | hold",
  "confidence": float,
  "reason": string
}}

Market Data:
{json.dumps(data, indent=2)}

Rules:
- No explanation outside JSON
- No markdown
- No extra text
"""

    # -----------------------------
    # OLLAMA CALL
    # -----------------------------

    def _query_ollama(self, prompt: str) -> str:
        result = subprocess.run(
            ["ollama", "run", self.model],
            input=prompt,
            text=True,
            capture_output=True
        )

        return result.stdout.strip()

    # -----------------------------
    # SAFE PARSER (CRITICAL)
    # -----------------------------

    def _parse_response(self, raw: str) -> Dict[str, Any]:
        try:
            data = json.loads(raw)

            return {
                "action": data.get("action", "hold"),
                "confidence": float(data.get("confidence", 0.0)),
                "reason": data.get("reason", "")
            }

        except Exception:
            # HARD FAIL SAFE
            return {
                "action": "hold",
                "confidence": 0.0,
                "reason": "invalid_llm_response"
            }
