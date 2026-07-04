from spine.L4_runtime.compiler.contract_diff_engine import compute_contract_diff
from spine.L4_runtime.compiler.contract_patch_engine import generate_contract_patch_plan
def test_contract_diff():
    r = compute_contract_diff(limit=200)
    assert "missing" in r
    assert "extra" in r
def test_patch_plan():
    r = generate_contract_patch_plan(limit=200)
    assert "patch_plan" in r
    assert "total_steps" in r
