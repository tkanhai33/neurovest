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
