from spine.L4_runtime.orchestrator.intelligent_roadmap_engine import generate_intelligent_roadmap
def test_intelligent_roadmap():
    r = generate_intelligent_roadmap(limit=200)
    assert "next" in r or "message" in r
