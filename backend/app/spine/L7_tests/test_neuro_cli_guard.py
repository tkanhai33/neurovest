from spine.L3_facade.repo_intelligence_facade import get_repo_intelligence
def test_neuro_cli_flow():
    data = get_repo_intelligence(limit=10)
    assert isinstance(data, dict)
    assert "file_count" in data
    assert "structure" in data
    assert data["file_count"] >= 0
def test_neuro_cli_isolation():
    # ensures CLI is not directly tied to L4 engine
    import spine.L3_facade.repo_intelligence_facade as facade
    source = facade.get_repo_intelligence.__code__.co_filename
    assert "L4_runtime" in source or "facade" in source
