from spine.L4_runtime.patch_executor import run_patch_cycle
from spine.L4_runtime.convergence_engine import check_convergence
from spine.L4_runtime.autonomous_repair_loop import run_autonomous_loop
def test_patch_executor_runs():
    r = run_patch_cycle(limit=200)
    assert "applied_count" in r
def test_convergence_engine_runs():
    c = check_convergence(limit=200)
    assert "converged" in c
def test_autonomous_loop_runs():
    r = run_autonomous_loop(limit=200)
    assert "cycles_run" in r
    assert "final_state" in r
