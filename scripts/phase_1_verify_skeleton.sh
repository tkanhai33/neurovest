#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Checking NeuroVest skeleton..."

test -d backend/app/stacks
test -d frontend/src/features
test -d docs/contracts
test -f .env.example
test -f backend/app/main.py

grep -q "PostgreSQL" backend/README.md
grep -q "BROKER_ENABLED=false" .env.example
grep -q "LIVE_TRADING_ENABLED=false" .env.example

echo "PASS: Phase 1 skeleton structure exists and safety defaults are locked."
