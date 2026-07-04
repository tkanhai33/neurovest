#!/bin/bash

set -e

echo "======================================"
echo "🧠 NEURO CORE BOOT SEQUENCE"
echo "======================================"

export PYTHONPATH=.

echo "➡ Running architecture CLI..."

python3 backend/app/llm_bridge/core/cli/neuro.py
