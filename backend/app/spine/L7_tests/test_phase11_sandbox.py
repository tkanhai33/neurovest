from spine.L4_runtime.sandbox.simulation_engine import simulate_change
from spine.L4_runtime.sandbox.simulation_batch_runner import run_sandbox
from spine.L4_runtime.sandbox.safe_commit_planner import compute_safe_commit
def test_simulation_engine_runs():
    r = simulate_change({"stack": "risk", "target": "limits"})
    assert "risk_score" in r
    assert "safe" in r
def test_sandbox_batch_runner():
    r = run_sandbox(limit=200)
    assert "total" in r
def test_safe_commit_planner():
    r = compute_safe_commit(limit=200)
    assert "safe_commit_count" in r
