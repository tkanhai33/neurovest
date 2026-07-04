from spine.L4_runtime.repo_intelligence_engine import classify_stack
from spine.L3_facade.repo_intelligence_facade import get_repo_intelligence
from spine.L4_runtime.refactor_manifest_engine import build_refactor_manifest
def test_execution_broker_classifies_as_execution():
    assert classify_stack("backend/app/stacks/execution/broker.py") == "execution"
def test_stack_path_wins_before_keyword():
    assert classify_stack("backend/app/stacks/execution/broker.py") != "snaptrade"
def test_phase8_intelligence_runs():
    data = get_repo_intelligence(limit=300)
    assert "execution" in data["structure"]
def test_refactor_manifest_is_manifest_only():
    m = build_refactor_manifest(limit=300)
    assert m["safe_to_apply"] is False
