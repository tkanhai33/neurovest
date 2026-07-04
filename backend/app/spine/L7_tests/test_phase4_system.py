from spine.L4_runtime.dependency_graph_engine import build_dependency_graph
from spine.L4_runtime.runtime_wiring_validator import validate_runtime_wiring
from spine.L4_runtime.implementation_planner_v4 import compute_next_implementation
def test_dependency_graph_builds():
    g = build_dependency_graph(limit=200)
    assert "graph" in g
    assert "missing_links" in g
def test_wiring_validator_runs():
    v = validate_runtime_wiring(limit=200)
    assert "violations" in v
    assert "orphan_stacks" in v
def test_implementation_planner_runs():
    p = compute_next_implementation(limit=200)
    assert "next_stack" in p
    assert "next_file" in p
