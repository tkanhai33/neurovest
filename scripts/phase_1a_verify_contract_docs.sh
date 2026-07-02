#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

required=(
docs/contracts/MASTER_ARCHITECTURE_CONTRACT.md
docs/contracts/STACK_OWNERSHIP_MAP.md
docs/contracts/FORBIDDEN_CALL_RULES.md
docs/contracts/BUILD_ORDER_PHASE_GATE_CONTRACT.md
docs/contracts/FREE_PROVIDER_PRODUCT_DIRECTION_CONTRACT.md
docs/contracts/SYSTEM_CONTEXT_DATA_FLOW_CONTRACT.md
docs/contracts/REPOSITORY_BLUEPRINT_CONTRACT.md
docs/contracts/LOCAL_SYSTEM_RESOURCE_CONTRACT.md
docs/contracts/MVP_DEFAULTS_CONTRACT.md
docs/contracts/DATABASE_DEFAULT_UPDATE.md
docs/contracts/FINAL_CONTRACT_CHECKLIST.md
)

for file in "${required[@]}"; do
test -f "$file"
done

grep -q "PostgreSQL" docs/contracts/MVP_DEFAULTS_CONTRACT.md
grep -q "Ollama" docs/contracts/FREE_PROVIDER_PRODUCT_DIRECTION_CONTRACT.md
grep -q "No live trading" docs/contracts/MASTER_ARCHITECTURE_CONTRACT.md
grep -q "Phase 1 is skeleton-only" docs/contracts/FINAL_CONTRACT_CHECKLIST.md

echo "PASS: Phase 1A full contract documents written and verified."
