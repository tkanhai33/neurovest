from backend.app.stacks.chat_public.developer_repository_inspection import (
    inspect_repository,
)


def test_finds_actual_developer_source():
    result = inspect_repository(
        "developer_response_builder build_developer_response"
    )
    assert "Repository source matches" in result
    assert "developer_response_builder.py" in result


def test_short_uninformative_query_returns_empty():
    assert inspect_repository("the and for") == ""


def test_source_tool_does_not_offer_mutation():
    from backend.app.stacks.chat_public import developer_repository_inspection as module

    assert not hasattr(module, "apply_patch")
    assert not hasattr(module, "execute_command")
    assert not hasattr(module, "write_file")
