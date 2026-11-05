
from pathlib import Path
import ast

from backend.app.stacks.chat_public import chat_runtime


def runtime_source():
    path = Path(chat_runtime.__file__)
    return path.read_text("utf-8")


def test_v5_selection_only_after_success():
    source = runtime_source()
    tree = ast.parse(source)

    review = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.If)
        and isinstance(node.test, ast.Name)
        and node.test.id == "_self_review_exact"
    ]

    assert len(review) == 1

    review_body = "\n".join(
        ast.unparse(item) for item in review[0].body
    )
    awareness_body = "\n".join(
        ast.unparse(item) for item in review[0].orelse
    )

    assert "_nv5_selected = True" in awareness_body
    assert "_nv5_selected = True" not in review_body

    assert awareness_body.index(
        "if _nv5_answer is not None"
    ) < awareness_body.index(
        "_nv5_selected = True"
    )


def test_r10_and_v5_both_preserved():
    source = runtime_source()

    assert (
        'locals().get("_nv_r10_evidence_selected") is True'
        in source
    )
    assert (
        'locals().get("_nv5_selected") is True'
        in source
    )

    assert source.count(
        "_nv_r10_preserve_evidence = ("
    ) == 1

    assert "_v3_developer_role(principal)" in source


def test_general_relevance_not_applied_to_qualified_evidence():
    source = runtime_source()
    assert (
        'if _nv_qualified_developer_evidence:\n'
        '        _nv_relevance_status = "unchanged"'
    ) in source
    assert "await _nv_relevance_verify(" in source


def test_universe_reply_does_not_override_qualified_evidence():
    source = runtime_source()
    assert (
        '_verified_universe_reply is not None\n'
        '        and not _nv_qualified_developer_evidence'
    ) in source
    assert (
        'locals().get("_nv_r10_evidence_selected") is True'
    ) in source
    assert (
        'locals().get("_nv5_selected") is True'
    ) in source


def test_assistant_still_persisted_and_returned():
    source = runtime_source()
    tree = ast.parse(source)

    run = next(
        node for node in tree.body
        if isinstance(node, ast.AsyncFunctionDef)
        and node.name == "run_chat_turn"
    )

    body = ast.unparse(run)

    assert "content=assistant_content" in body
    assert "message=assistant_content" in body
    assert "await conversation_store.append_message(" in body


def test_v3_fallback_and_self_review_retained():
    source = runtime_source()

    assert "if _self_review_exact:" in source
    assert "_v3_result = await _v3_explain(" in source
    assert "if _nv5_answer is not None:" in source
