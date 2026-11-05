
"""Tests for the developer improvement journal."""

import ast
import runpy
from pathlib import Path

ROOT = Path.home() / "Neurovest"
SCRIPT = ROOT / "scripts/neuro_improvement_journal.py"

ns = runpy.run_path(
    str(SCRIPT),
    run_name="neuro_journal_test",
)

key = ns["observation_key"]
normalize = ns["normalize_finding"]
collect = ns["collect_findings"]


def test_source_is_valid_python():
    ast.parse(SCRIPT.read_text("utf-8"))


def test_deduplication_is_deterministic():
    assert key("module", "function", "large_function") == key(
        "module", "function", "large_function"
    )


def test_different_issues_have_different_keys():
    assert key("module", "function", "large_function") != key(
        "module", "function", "missing_docstring"
    )


def test_static_finding_normalization():
    result = normalize(
        "developer_self_review",
        {
            "function": "inventory_module",
            "type": "large_function",
            "priority": "P2",
            "evidence": "Function spans 100 lines",
            "recommendation": "Extract independent responsibilities",
        },
        "a" * 64,
    )

    assert result["module"] == "developer_self_review"
    assert result["function"] == "inventory_module"
    assert result["priority"] == "P2"


def test_invalid_priority_defaults_to_p3():
    result = normalize(
        "module",
        {"priority": "UNKNOWN", "type": "test"},
        "a" * 64,
    )
    assert result["priority"] == "P3"


def test_bounded_scan_uses_existing_allowlist():
    from backend.app.stacks.chat_public.developer_self_review import (
        ALLOWED_MODULES,
    )

    report = collect()

    assert len(report["modules"]) <= len(ALLOWED_MODULES)
    assert report["allowed_count"] == len(ALLOWED_MODULES)
    assert all(
        item in ALLOWED_MODULES
        for item in report["modules"]
    )


def test_no_http_routes_or_patch_execution():
    source = SCRIPT.read_text("utf-8")

    assert "@router." not in source
    assert "apply_unified_diff" not in source
    assert "handle_developer_command" not in source
    assert "subprocess.run" not in source


def test_postgres_tables_are_namespaced():
    assert "neuro_developer_improvement_runs_v1" in ns["CREATE_RUNS"]
    assert "neuro_developer_improvement_findings_v1" in ns["CREATE_FINDINGS"]
