#!/bin/bash

set -e

cd backend/app
export PYTHONPATH=.

echo "🧠 NEURO ENGINE STARTED"

python3 spine/L5_api/neuro_autonomous_engine_v3.py "$@"
