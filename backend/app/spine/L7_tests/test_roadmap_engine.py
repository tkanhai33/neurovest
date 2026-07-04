from spine.L4_runtime.roadmap_engine import generate_roadmap
def test_roadmap():
    r = generate_roadmap(limit=200)
    assert "next" in r or "message" in r
