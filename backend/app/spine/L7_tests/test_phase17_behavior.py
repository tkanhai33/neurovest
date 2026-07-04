from spine.L4_runtime.behavior.behavior_analyzer import analyze_behavior
from spine.L4_runtime.behavior.behavior_roadmap_engine import generate_behavior_roadmap
def test_behavior_analyzer():
    r = analyze_behavior(limit=200)
    assert "silent_stacks" in r
def test_behavior_roadmap():
    r = generate_behavior_roadmap(limit=200)
    assert "next" in r or "roadmap" in r
