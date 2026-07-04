#!/bin/bash
set -e

echo "🧠 Phase 9 — Architecture Certification Layer"

mkdir -p backend/app/spine/L4_runtime/certification
mkdir -p backend/app/spine/L5_api
mkdir -p backend/app/spine/L7_tests

cat > backend/app/spine/L4_runtime/architecture_fingerprint.py <<'PY'
from __future__ import annotations

import hashlib
import json
from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence
from spine.L4_runtime.dependency_graph_engine import build_dependency_graph
from spine.L4_runtime.convergence_engine import check_convergence

def build_architecture_fingerprint(limit: int = 1000) -> dict:
    payload = {
        "repo": build_repo_intelligence(limit=limit)["summary"],
        "deps": build_dependency_graph(limit=limit)["graph"],
        "convergence": check_convergence(limit=limit),
    }

    encoded = json.dumps(payload, sort_keys=True).encode()
    digest = hashlib.sha256(encoded).hexdigest()

    return {
        "fingerprint": digest,
        "payload": payload,
    }

if __name__ == "__main__":
    print(json.dumps(build_architecture_fingerprint(), indent=2))
PY

cat > backend/app/spine/L4_runtime/architecture_certifier.py <<'PY'
from __future__ import annotations

import json
from pathlib import Path

from spine.L4_runtime.architecture_fingerprint import build_architecture_fingerprint
from spine.L4_runtime.convergence_engine import check_convergence
from spine.L4_runtime.refactor_manifest_engine import build_refactor_manifest

ROOT = Path(".").resolve()
CERT_DIR = ROOT / "backend/app/spine/L4_runtime/certification"
CERT_FILE = CERT_DIR / "architecture_certified_baseline.json"

def certify_architecture(limit: int = 1000) -> dict:
    convergence = check_convergence(limit=limit)
    manifest = build_refactor_manifest(limit=limit)
    fingerprint = build_architecture_fingerprint(limit=limit)

    certified = bool(convergence["converged"] and manifest["safe_to_apply"] is False)

    result = {
        "certified": certified,
        "reason": "Architecture converged and mutation manifest is locked",
        "fingerprint": fingerprint["fingerprint"],
        "convergence": convergence,
        "refactor_manifest_safe_to_apply": manifest["safe_to_apply"],
    }

    CERT_DIR.mkdir(parents=True, exist_ok=True)
    CERT_FILE.write_text(json.dumps(result, indent=2))

    return result

if __name__ == "__main__":
    print(json.dumps(certify_architecture(), indent=2))
PY

cat > backend/app/spine/L4_runtime/architecture_drift_detector.py <<'PY'
from __future__ import annotations

import json
from pathlib import Path

from spine.L4_runtime.architecture_fingerprint import build_architecture_fingerprint

ROOT = Path(".").resolve()
CERT_FILE = ROOT / "backend/app/spine/L4_runtime/certification/architecture_certified_baseline.json"

def detect_architecture_drift(limit: int = 1000) -> dict:
    current = build_architecture_fingerprint(limit=limit)

    if not CERT_FILE.exists():
        return {
            "baseline_exists": False,
            "drift_detected": True,
            "reason": "No certified architecture baseline exists",
            "current_fingerprint": current["fingerprint"],
        }

    baseline = json.loads(CERT_FILE.read_text())
    drift = baseline.get("fingerprint") != current["fingerprint"]

    return {
        "baseline_exists": True,
        "drift_detected": drift,
        "baseline_fingerprint": baseline.get("fingerprint"),
        "current_fingerprint": current["fingerprint"],
    }

if __name__ == "__main__":
    print(json.dumps(detect_architecture_drift(), indent=2))
PY

cat > backend/app/spine/L5_api/repo_intelligence_v9_cli.py <<'PY'
from __future__ import annotations

import json

from spine.L4_runtime.architecture_certifier import certify_architecture
from spine.L4_runtime.architecture_drift_detector import detect_architecture_drift
from spine.L4_runtime.architecture_fingerprint import build_architecture_fingerprint

def run(limit: int = 1000):
    report = {
        "fingerprint": build_architecture_fingerprint(limit=limit),
        "certification": certify_architecture(limit=limit),
        "drift_check": detect_architecture_drift(limit=limit),
    }

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run()
PY

cat > backend/app/spine/L7_tests/test_phase9_certification.py <<'PY'
from spine.L4_runtime.architecture_fingerprint import build_architecture_fingerprint
from spine.L4_runtime.architecture_certifier import certify_architecture
from spine.L4_runtime.architecture_drift_detector import detect_architecture_drift

def test_architecture_fingerprint_builds():
    f = build_architecture_fingerprint(limit=300)
    assert "fingerprint" in f
    assert len(f["fingerprint"]) == 64

def test_architecture_certifier_runs():
    c = certify_architecture(limit=300)
    assert "certified" in c
    assert "fingerprint" in c

def test_architecture_drift_detector_runs():
    d = detect_architecture_drift(limit=300)
    assert "drift_detected" in d
PY

echo "🧠 Running Phase 9 CLI..."
PYTHONPATH=backend/app python3 backend/app/spine/L5_api/repo_intelligence_v9_cli.py

echo "🧪 Running Phase 9 tests..."
PYTHONPATH=backend/app pytest -q backend/app/spine/L7_tests/test_phase9_certification.py

echo "✅ Phase 9 Complete"
