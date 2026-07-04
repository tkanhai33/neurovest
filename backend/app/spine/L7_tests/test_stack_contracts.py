from spine.L3_facade.repo_intelligence_facade import get_repo_intelligence
from spine.L4_runtime.stack_gap_analyzer import analyze_stack_gaps
from spine.L4_runtime.next_file_planner import compute_next_file
def test_repo_intelligence_runs():
    data = get_repo_intelligence(limit=200)
    assert "structure" in data
def test_stack_gap_analyzer_runs():
    gaps = analyze_stack_gaps(limit=200)
    assert "gaps" in gaps
def test_next_file_planner_runs():
    result = compute_next_file(limit=200)
    assert "next_file" in result
    assert "reason" in result
