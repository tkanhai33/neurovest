from spine.L4_runtime.roadmap.validated_roadmap_engine import generate_validated_roadmap
def test_validated_roadmap():
    r = generate_validated_roadmap(limit=200)
    assert "next_action" in r or "message" in r
