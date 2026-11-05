"""Bounded, read-only NeuroVest Python function self-review.

This module inventories functions using AST without importing or
executing target source files.

Findings are static-analysis recommendations, not verified defects.
"""

from __future__ import annotations

import ast
import hashlib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CODE_ROOT = ROOT / "backend/app"

ALLOWED_MODULES = {
    "developer_repository_inspection":
        "backend/app/stacks/chat_public/developer_repository_inspection.py",
    "developer_chat_commands":
        "backend/app/stacks/chat_public/developer_chat_commands.py",
    "developer_role_guard":
        "backend/app/stacks/chat_public/developer_role_guard.py",
    "developer_self_review": "backend/app/stacks/chat_public/developer_self_review.py",
}

MAX_SOURCE_BYTES = 50000
MAX_FUNCTIONS = 120


@dataclass(frozen=True)
class Finding:
    priority: int
    line: int
    function: str
    category: str
    evidence: str
    recommendation: str


def _target_path(module_name: str) -> Path:
    if module_name not in ALLOWED_MODULES:
        raise ValueError("Module is outside the self-review scope.")

    path = ROOT / ALLOWED_MODULES[module_name]
    resolved = path.resolve(strict=True)

    if not resolved.is_relative_to(CODE_ROOT.resolve()):
        raise ValueError("Module path escapes the application source.")

    if not resolved.is_file() or path.is_symlink():
        raise ValueError("Module is not a regular source file.")

    if resolved.stat().st_size > MAX_SOURCE_BYTES:
        raise ValueError("Source exceeds review size limit.")

    return resolved


def _all_functions(tree: ast.AST):
    functions = []

    def visit(body, prefix=""):
        for node in body:
            if isinstance(
                node, (ast.FunctionDef, ast.AsyncFunctionDef)
            ):
                name = prefix + node.name
                functions.append((name, node))

                # Nested functions are explicitly inventoried.
                visit(node.body, name + ".")

            elif isinstance(node, ast.ClassDef):
                visit(node.body, prefix + node.name + ".")

    visit(tree.body)

    return functions[:MAX_FUNCTIONS]


def _has_docstring(node) -> bool:
    return bool(ast.get_docstring(node))


def _complexity(node) -> int:
    score = 1

    for child in ast.walk(node):
        if child is node:
            continue

        if isinstance(child, (
            ast.If,
            ast.For,
            ast.AsyncFor,
            ast.While,
            ast.Try,
            ast.ExceptHandler,
            ast.With,
            ast.AsyncWith,
            ast.IfExp,
            ast.Match,
        )):
            score += 1

        if isinstance(child, ast.BoolOp):
            score += max(0, len(child.values) - 1)

    return score


def _exception_swallowing(node) -> list[int]:
    locations = []

    for child in ast.walk(node):
        if isinstance(child, ast.ExceptHandler):
            if (
                len(child.body) == 1
                and isinstance(child.body[0], ast.Pass)
            ):
                locations.append(child.lineno)

    return locations


def inventory_module(module_name: str) -> dict:
    """
    Inventory functions in the specified module using AST-based analysis.

    Args:
        module_name (str): The name of the module to inventory.

    Returns:
        dict: A dictionary containing inventory results and findings.

    Raises:
        ValueError: If the module is not allowed or exceeds size limits.
    """

    path = _target_path(module_name)
    content = path.read_text(encoding="utf-8")

    tree = ast.parse(content, filename=str(path))
    functions = _all_functions(tree)

    findings = []
    records = []

    for name, node in functions:
        start = node.lineno
        end = node.end_lineno or start
        size = end - start + 1
        complexity = _complexity(node)

        records.append({
            "name": name,
            "line": start,
            "end_line": end,
            "lines": size,
            "complexity": complexity,
            "documented": _has_docstring(node),
        })

        if size >= 80:
            findings.append(Finding(
                priority=2,
                line=start,
                function=name,
                category="large_function",
                evidence=f"Function spans {size} source lines.",
                recommendation=(
                    "Review whether independent responsibilities "
                    "can be extracted into smaller functions."
                ),
            ))

        if complexity >= 15:
            findings.append(Finding(
                priority=1,
                line=start,
                function=name,
                category="branch_complexity",
                evidence=(
                    f"Estimated static branch complexity: "
                    f"{complexity}."
                ),
                recommendation=(
                    "Review complex branches and add focused "
                    "tests before simplifying control flow."
                ),
            ))

        if not _has_docstring(node) and not name.startswith("_"):
            findings.append(Finding(
                priority=3,
                line=start,
                function=name,
                category="missing_docstring",
                evidence="Public function has no docstring.",
                recommendation=(
                    "Document the function's purpose and "
                    "important input/output contracts."
                ),
            ))

        for line in _exception_swallowing(node):
            findings.append(Finding(
                priority=1,
                line=line,
                function=name,
                category="silent_exception",
                evidence=(
                    f"Exception handler at line {line} "
                    "contains only pass."
                ),
                recommendation=(
                    "Review whether failures should be logged, "
                    "handled explicitly, or propagated."
                ),
            ))

    findings.sort(
        key=lambda finding: (
            finding.priority,
            finding.line,
            finding.function,
        )
    )

    return {
        "module": module_name,
        "file": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(content.encode()).hexdigest(),
        "function_count": len(records),
        "functions": records,
        "findings": [
            {
                "priority": finding.priority,
                "line": finding.line,
                "function": finding.function,
                "category": finding.category,
                "evidence": finding.evidence,
                "recommendation": finding.recommendation,
            }
            for finding in findings
        ],
    }


def render_review(module_name: str) -> str:
    """Render a read-only developer function review for an allowed module."""
    try:
        report = inventory_module(module_name)
    except (ValueError, OSError, SyntaxError) as exc:
        return "Neuro self-review unavailable: " + str(exc)

    lines = [
        "## Neuro Developer — Function Self-Review",
        "",
        f"**Module:** `{report['module']}`",
        f"**File:** `{report['file']}`",
        f"**Functions inventoried:** {report['function_count']}",
        f"**Source SHA256:** `{report['sha256']}`",
        "",
        "### Prioritized improvement candidates",
        "",
    ]

    findings = report["findings"]

    if not findings:
        lines.append(
            "No findings from the current static-analysis rules. "
            "This does not establish that the module is defect-free."
        )

    for index, finding in enumerate(findings[:15], 1):
        lines.extend([
            (
                f"{index}. **P{finding['priority']} — "
                f"{finding['category']}**"
            ),
            (
                f"   - `{finding['function']}` "
                f"at line {finding['line']}"
            ),
            f"   - Evidence: {finding['evidence']}",
            f"   - Recommendation: {finding['recommendation']}",
        ])

    lines.extend([
        "",
        "**Assessment:** Static review only. Findings are "
        "improvement candidates, not confirmed bugs.",
        "",
        "**Code changes:** None.",
    ])

    # NEUROVEST_SELF_REVIEW_AI_FIXED_V1
    from backend.app.stacks.chat_public.developer_self_review_ai import render_ai_review
    return "\n".join(lines) + render_ai_review(module_name, report)
