#!/bin/bash

set -e

echo "======================================"
echo "⚡ NEURO FAST CHAT MODE"
echo "CACHED GRAPH + LOW LATENCY MODE"
echo "======================================"

export PYTHONPATH=.

python3 -u - <<'PY'
from backend.app.llm_bridge.cli_brain.neuro_cli import neuro

# =========================
# WARMUP (IMPORTANT)
# =========================
from backend.app.llm_bridge.context.cached_graph import get_graph
from backend.app.llm_bridge.context.cached_trace import get_trace

print("🧠 Warming system cache...")
get_graph()
get_trace()
print("✔ Ready\n")

while True:
    try:
        user_input = input("Neuro > ")
        if user_input.lower() in ["exit", "quit"]:
            break

        print("\n🧠 Neuro:\n")
        result = neuro(user_input)
        print("\n")

    except KeyboardInterrupt:
        break
PY
