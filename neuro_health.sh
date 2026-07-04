#!/bin/bash

echo "======================================"
echo "🧠 NEURO SYSTEM HEALTH CHECK (FIXED)"
echo "======================================"

echo ""
echo "🔍 Ollama binary check..."
if command -v ollama >/dev/null 2>&1; then
    echo "✔ Ollama found"
    which ollama
    ollama --version
else
    echo "❌ Ollama missing"
fi

echo ""
echo "🔍 Python integration test..."

python3 - <<PY
from backend.app.llm_bridge.cli_brain.ollama_safe import run_ollama_safe

print(run_ollama_safe("Say OK", "llama3.1"))
PY

echo ""
echo "======================================"
echo "🧠 HEALTH CHECK COMPLETE"
echo "======================================"
