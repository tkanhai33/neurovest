from spine.L4_runtime.governance.action_enforcer import enforce_action
from spine.L4_runtime.governance.state_auditor import audit_state
def test_enforcer_runs():
    r = enforce_action({"stack": "risk", "target": "limits"})
    assert "state" in r
def test_auditor_runs():
    r = audit_state()
    assert "state_snapshot" in r
