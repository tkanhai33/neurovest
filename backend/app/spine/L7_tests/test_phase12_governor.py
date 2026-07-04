from spine.L4_runtime.governance.decision_engine import evaluate_decision
from spine.L4_runtime.governance.approval_state_machine import run_approval_flow
def test_decision_engine():
    r = evaluate_decision({"stack": "risk", "target": "limits"})
    assert "approved" in r
def test_approval_flow():
    r = run_approval_flow({"stack": "strategy", "target": "selector"})
    assert "state" in r
    assert r["state"] in ["APPROVED", "REJECTED"]
