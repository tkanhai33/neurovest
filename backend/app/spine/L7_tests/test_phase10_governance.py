from spine.L4_runtime.governance.policy_engine import evaluate_policy
from spine.L4_runtime.governance.commit_gate import validate_commit
from spine.L4_runtime.governance.change_proposal_engine import generate_change_proposals
def test_policy_engine_runs():
    r = evaluate_policy({"stack": "risk", "target": "execution"})
    assert "allowed" in r
def test_proposal_generation():
    p = generate_change_proposals(limit=200)
    assert "proposals" in p
def test_commit_gate_runs():
    c = validate_commit(limit=200)
    assert "commit_allowed" in c
