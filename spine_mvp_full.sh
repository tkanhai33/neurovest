#!/bin/bash

set -e

echo "======================================"
echo "🧠 NEUROVEST SPINE BUILDER (REAL RUN)"
echo "======================================"

ROOT="backend/app"

LAYERS=(
  "spine/L7_tests"
  "spine/L6_frontend"
  "spine/L5_api"
  "spine/L4_runtime"
  "spine/L3_facade"
  "spine/L2_domain"
  "spine/L1_security"
  "spine/L0_adapters"
)

for layer in "${LAYERS[@]}"; do
  mkdir -p "$ROOT/$layer"
  touch "$ROOT/$layer/__init__.py"
done

STACKS=(
  "auth_identity"
  "market_data"
  "snaptrade"
  "strategy"
  "risk"
  "portfolio"
  "execution"
  "journal_ledger"
  "notification"
  "chat_public"
  "db_model"
)

for stack in "${STACKS[@]}"; do
  mkdir -p "$ROOT/stacks/$stack"
  touch "$ROOT/stacks/$stack/__init__.py"
done

echo ""
echo "✔ SPINE CREATED SUCCESSFULLY"
echo "✔ LAYERS READY"
echo "✔ STACKS READY"
echo "======================================"

echo ""
echo "TREE SNAPSHOT:"
find backend/app/spine backend/app/stacks -type d | sed 's/^/  /'
