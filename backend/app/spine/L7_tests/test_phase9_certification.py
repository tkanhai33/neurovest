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
