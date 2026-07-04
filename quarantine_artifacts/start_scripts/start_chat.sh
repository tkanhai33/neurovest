#!/bin/bash

export PYTHONPATH=backend/app
export TERM=dumb
export NO_COLOR=1

echo "======================================"
echo "🧠 NEURO SAFE CHAT MODE"
echo "DEPENDENCY GUARD ENABLED"
echo "======================================"

while true; do
  echo ""
  read -p "Neuro > " input

  if [[ "$input" == "exit" ]]; then
    break
  fi

  python3 -u - <<PY
from backend.app.llm_bridge.cli_brain.neuro_cli import neuro

result = neuro("""$input""")

print("\n🧠 Neuro:\n")
print(result)
PY

done
