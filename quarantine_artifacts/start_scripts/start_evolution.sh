#!/bin/bash

export PYTHONPATH=backend/app

echo "🧠 STARTING NEURO EVOLUTION LOOP"

python3 -u - <<PY
from backend.app.llm_bridge.cli_brain.evolution_engine import start_continuous_evolution

start_continuous_evolution(30)
PY
