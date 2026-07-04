#!/bin/bash

export PYTHONPATH=backend/app

echo "======================================"
echo "🧠 NEURO NEXT BUILD MODE"
echo "======================================"

python3 -u - <<PY
from backend.app.llm_bridge.cli_brain.next_build_cli import next_build

result = next_build()

print("\n🧠 WHAT SHOULD YOU BUILD NEXT:\n")
print(result["output"])
PY
