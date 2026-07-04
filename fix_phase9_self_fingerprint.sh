#!/bin/bash
set -e

echo "🧠 Fixing Phase 9 self-fingerprinting drift..."

python3 - <<'PY'
from pathlib import Path

p = Path("backend/app/spine/L2_domain/repo_intelligence/repo_scanner.py")
s = p.read_text()

s = s.replace(
'''    "quarantine_artifacts", "audit"''',
'''    "quarantine_artifacts", "audit",
    "snapshots", "applied_patches", "certification", "patches"'''
)

p.write_text(s)
PY

echo "🧪 Re-running Phase 9..."
PYTHONPATH=backend/app python3 backend/app/spine/L5_api/repo_intelligence_v9_cli.py

echo "🧪 Re-running tests..."
PYTHONPATH=backend/app pytest -q backend/app/spine/L7_tests/test_phase9_certification.py

echo "✅ Phase 9 fingerprint fix complete"
