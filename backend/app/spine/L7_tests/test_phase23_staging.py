from spine.L4_runtime.compiler.staging_engine import build_staged_plan
from spine.L4_runtime.compiler.execution_gate import validate_stage
def test_staging():
    r = build_staged_plan(limit=200)
    assert "stages" in r
def test_gate():
    r = validate_stage({"stack": "risk", "files": []})
    assert "approved" in r
