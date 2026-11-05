
import ast
import difflib
import runpy
from pathlib import Path

ROOT = Path.home() / "Neurovest"
RELATIVE = (
    "backend/app/stacks/chat_public/"
    "developer_repository_inspection.py"
)

preview = runpy.run_path(
    str(ROOT / "scripts/neuro_developer_patch_preview.py")
)
applier = runpy.run_path(
    str(ROOT / "scripts/neuro_developer_patch_apply.py")
)

source = Path(__file__).with_name("pre_refactor_fixture.py").read_text(encoding="utf-8")
build = preview["build_sensitive_refactor"]
validate = preview["validate_patch"]


def candidate():
    return validate(source, build(source))


def test_exact_two_edits():
    proposal = build(source)
    assert len(proposal["edits"]) == 2
    assert all(
        source.count(edit["old"]) == 1
        for edit in proposal["edits"]
    )


def test_helper_and_call_are_present():
    result = candidate()
    tree = ast.parse(result)

    functions = {
        node.name: node for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }

    assert "_is_sensitive_term" in functions
    assert "inspect_repository" in functions

    calls = [
        node for node in ast.walk(functions["inspect_repository"])
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_is_sensitive_term"
    ]

    assert len(calls) == 1


def test_helper_preserves_original_filter_ast():
    original_tree = ast.parse(source)
    result_tree = ast.parse(candidate())

    original_function = next(
        node for node in original_tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "inspect_repository"
    )

    old_filter = next(
        node.test for node in ast.walk(original_function)
        if isinstance(node, ast.If)
        and isinstance(node.test, ast.Call)
        and isinstance(node.test.func, ast.Name)
        and node.test.func.id == "any"
        and "stripped.lower()" in (
            ast.get_source_segment(source, node.test) or ""
        )
    )

    helper = next(
        node for node in result_tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "_is_sensitive_term"
    )

    new_expression = next(
        node.value for node in helper.body
        if isinstance(node, ast.Return)
    )

    assert ast.dump(
        old_filter, include_attributes=False
    ) == ast.dump(
        new_expression, include_attributes=False
    )


def test_diff_compatible_with_existing_applier():
    result = candidate()

    diff = "".join(difflib.unified_diff(
        source.splitlines(keepends=True),
        result.splitlines(keepends=True),
        fromfile="a/" + RELATIVE,
        tofile="b/" + RELATIVE,
    ))

    rebuilt = applier["apply_unified_diff"](
        source, diff, RELATIVE
    )

    assert rebuilt == result


def test_unexpected_source_rejected():
    try:
        build("def inspect_repository(query):\n    return query\n")
    except ValueError:
        pass
    else:
        raise AssertionError("Unexpected source accepted")


def test_refactor_selection_is_narrow():
    select = preview["use_sensitive_refactor"]
    task = "Refactor credential detection into _is_sensitive_term"

    assert select(task, RELATIVE)
    assert not select("Increase max_files", RELATIVE)
    assert not select(task, "backend/app/main.py")


def test_no_application_source_mutation():
    path = ROOT / RELATIVE
    before = path.read_bytes()
    candidate()
    assert path.read_bytes() == before
