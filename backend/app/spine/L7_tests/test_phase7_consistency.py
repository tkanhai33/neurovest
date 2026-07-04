from spine.L4_runtime.canonical_truth_engine import build_canonical_state
from spine.L4_runtime.gap_reconciliation_engine import reconcile_gaps
from spine.L4_runtime.consistency_validator import validate_consistency
def test_canonical_state():
    c = build_canonical_state(limit=200)
    assert "canonical_state" in c
def test_gap_reconciliation():
    g = reconcile_gaps(limit=200)
    assert "corrected_gaps" in g
def test_consistency_validator():
    v = validate_consistency(limit=200)
    assert "is_consistent" in v
