from spine.L4_runtime.stack_scaffold_generator import generate_from_repo
def test_scaffold_generation_runs():
    result = generate_from_repo(limit=200)
    assert "scaffolds" in result
    assert isinstance(result["scaffolds"], list)
def test_scaffold_structure():
    if result["scaffolds"]:
        first = result["scaffolds"][0]
        assert "generated_files" in first
        assert "stack" in first
