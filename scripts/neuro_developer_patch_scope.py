
"""AST-based scope enforcement for developer code proposals.

This does not prove semantic correctness. It checks that requested,
explicitly named function and docstring boundaries are respected.
"""

from __future__ import annotations

import ast
import copy
import re


def _dump(node):
    return ast.dump(node, include_attributes=False)


def _functions(tree):
    return {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def _without_docstring(node):
    clone = copy.deepcopy(node)

    if (
        clone.body
        and isinstance(clone.body[0], ast.Expr)
        and isinstance(clone.body[0].value, ast.Constant)
        and isinstance(clone.body[0].value.value, str)
    ):
        clone.body.pop(0)

    return clone


def _module_without_target(tree, target):
    clone = copy.deepcopy(tree)

    for index, node in enumerate(clone.body):
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == target
        ):
            clone.body[index] = ast.Pass()
            return clone

    raise ValueError("Requested function not found.")


def _requested_function(task, tree):
    names = _functions(tree)

    mentioned = [
        name for name in names
        if re.search(
            r"(?<![A-Za-z0-9_])"
            + re.escape(name)
            + r"(?![A-Za-z0-9_])",
            task,
        )
    ]

    if len(mentioned) > 1:
        raise ValueError(
            "SCOPE_REJECTED: multiple function targets; "
            "a single-function scope is required."
        )

    if not mentioned:
        return None

    return mentioned[0]


def _has_docstring(node):
    return (
        bool(node.body)
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
        and isinstance(node.body[0].value.value, str)
    )


def enforce_patch_scope(original, candidate, task):
    """Reject changes outside an explicitly requested function scope.

    Returns a status string identifying the applied policy.
    """

    if not isinstance(task, str) or not task.strip():
        raise ValueError("SCOPE_REJECTED: missing development task.")

    before = ast.parse(original)
    after = ast.parse(candidate)

    extraction_status = _validate_helper_extraction(
        before, after, task
    )
    if extraction_status is not None:
        return extraction_status

    target = _requested_function(task, before)
    lower = task.casefold()

    docstring_request = (
        "docstring" in lower
        or "documentation" in lower
    )

    scope_request = any(
        phrase in lower
        for phrase in (
            "only",
            "inside",
            "within",
            "function named",
            "function called",
            "function body",
            "immediately after its def",
            "preserve all other",
            "do not modify any other",
        )
    )

    if target is None:
        if docstring_request or scope_request:
            raise ValueError(
                "SCOPE_REJECTED: constrained task has "
                "no uniquely identified existing function."
            )
        return "NO_EXPLICIT_FUNCTION_SCOPE"

    before_functions = _functions(before)
    after_functions = _functions(after)

    if target not in after_functions:
        raise ValueError(
            "SCOPE_REJECTED: requested function was removed."
        )

    old_function = before_functions[target]
    new_function = after_functions[target]

    if docstring_request:
        if (
            _dump(_module_without_target(before, target))
            != _dump(_module_without_target(after, target))
        ):
            raise ValueError(
                "SCOPE_REJECTED: docstring proposal "
                "modified code outside the requested function."
            )

        if not _has_docstring(new_function):
            raise ValueError(
                "SCOPE_REJECTED: requested function "
                "has no resulting docstring."
            )

        if (
            _dump(_without_docstring(old_function))
            != _dump(_without_docstring(new_function))
        ):
            raise ValueError(
                "SCOPE_REJECTED: docstring proposal "
                "modified executable statements or signature."
            )

        if (
            _has_docstring(old_function)
            and ast.get_docstring(old_function)
            == ast.get_docstring(new_function)
        ):
            raise ValueError(
                "SCOPE_REJECTED: requested function "
                "docstring did not change."
            )

        return "TARGET_FUNCTION_DOCSTRING_ONLY"

    if scope_request:
        if (
            _dump(_module_without_target(before, target))
            != _dump(_module_without_target(after, target))
        ):
            raise ValueError(
                "SCOPE_REJECTED: proposal modified "
                "code outside requested function."
            )

        if _dump(old_function) == _dump(new_function):
            raise ValueError(
                "SCOPE_REJECTED: requested function did not change."
            )

        return "TARGET_FUNCTION_ONLY"

    return "FUNCTION_IDENTIFIED_NO_EXCLUSIVE_SCOPE"


# NEUROVEST_HELPER_EXTRACTION_SCOPE_V1

def _helper_extraction_task(task):
    """Require an exact target/helper extraction contract."""
    import re

    if not task.startswith("AUTO_REVIEW_EXTRACT_HELPER:"):
        return None

    match = re.fullmatch(
        r"AUTO_REVIEW_EXTRACT_HELPER:"
        r"([A-Za-z_][A-Za-z0-9_]*):"
        r"(_[A-Za-z][A-Za-z0-9_]*)",
        task,
    )

    if match is None:
        raise ValueError(
            "SCOPE_REJECTED: malformed helper extraction contract."
        )

    return match.groups()


def _validate_helper_extraction(before, after, task):
    """Allow one existing function and one new private helper."""
    import copy

    contract = _helper_extraction_task(task)

    if contract is None:
        return None

    target, helper = contract

    old_functions = _functions(before)
    new_functions = _functions(after)

    if target == helper:
        raise ValueError("SCOPE_REJECTED: helper equals target.")

    if target not in old_functions or target not in new_functions:
        raise ValueError("SCOPE_REJECTED: target function missing.")

    if helper in old_functions:
        raise ValueError("SCOPE_REJECTED: helper already exists.")

    new_helper_nodes = [
        node for node in after.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == helper
    ]

    if (
        len(new_helper_nodes) != 1
        or not isinstance(new_helper_nodes[0], ast.FunctionDef)
    ):
        raise ValueError(
            "SCOPE_REJECTED: exactly one synchronous helper required."
        )

    helper_node = new_helper_nodes[0]

    if helper_node.decorator_list:
        raise ValueError("SCOPE_REJECTED: helper decorators forbidden.")

    if helper.startswith("__"):
        raise ValueError("SCOPE_REJECTED: dunder helper forbidden.")

    if any(
        isinstance(
            node,
            (ast.Global, ast.Nonlocal, ast.Import, ast.ImportFrom),
        )
        for node in ast.walk(helper_node)
    ):
        raise ValueError(
            "SCOPE_REJECTED: helper imports and global declarations forbidden."
        )

    # Prevent collisions with existing classes or other definitions.
    existing_names = {
        node.name for node in before.body
        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
        )
    }

    if helper in existing_names:
        raise ValueError("SCOPE_REJECTED: existing name collision.")

    def excluding(tree, names):
        clone = copy.deepcopy(tree)
        clone.body = [
            node for node in clone.body
            if not (
                isinstance(
                    node, (ast.FunctionDef, ast.AsyncFunctionDef)
                )
                and node.name in names
            )
        ]
        return ast.dump(clone, include_attributes=False)

    if excluding(before, {target}) != excluding(
        after, {target, helper}
    ):
        raise ValueError(
            "SCOPE_REJECTED: unrelated module changes detected."
        )

    old_target = old_functions[target]
    new_target = new_functions[target]

    old_interface = copy.deepcopy(old_target)
    new_interface = copy.deepcopy(new_target)

    old_interface.body = [ast.Pass()]
    new_interface.body = [ast.Pass()]

    if _dump(old_interface) != _dump(new_interface):
        raise ValueError(
            "SCOPE_REJECTED: existing function interface changed."
        )

    if _dump(old_target) == _dump(new_target):
        raise ValueError(
            "SCOPE_REJECTED: requested function did not change."
        )

    if not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == helper
        for node in ast.walk(new_target)
    ):
        raise ValueError(
            "SCOPE_REJECTED: target does not call new helper."
        )

    return "TARGET_FUNCTION_PLUS_ONE_PRIVATE_HELPER"
