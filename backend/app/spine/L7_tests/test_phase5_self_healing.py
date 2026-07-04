from spine.L4_runtime.architecture_repair_engine import detect_repair_actions
from spine.L4_runtime.stack_rebalancer import compute_rebalance_actions
from spine.L4_runtime.architecture_diff_engine import compute_architecture_diff
def test_repair_engine_runs():
    r = detect_repair_actions(limit=200)
    assert "repairs" in r
def test_rebalancer_runs():
    r = compute_rebalance_actions(limit=200)
    assert "rebalance_actions" in r
def test_diff_engine_runs():
    d = compute_architecture_diff(limit=200)
    assert "missing_components" in d
    assert "broken_dependencies" in d
