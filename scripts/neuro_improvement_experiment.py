#!/usr/bin/env python3
"""Bounded NeuroVest developer improvement experiment, v1.

Runs only the explicitly pinned candidate. Never applies patches.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE_SOURCE = ROOT / "backend/app/stacks/chat_public/developer_chat_commands.py"
SOURCE = ROOT / "runtime/developer_patch_backups/" / "experiment_chat_integration_20261012_132150_710935" / "developer_chat_commands.original.py"
EXPECTED_BASELINE_HASH = "1a312b0d78c0f74dd52c0f94b76f72aaf644c4f42b11ddbb4fd57768a88202f6"
EXPECTED_INTEGRATED_HASH = "679897aceb6ab1366882afd69753fbbdd26b924de87d8a1b15f9120e1834cd83"
FOLDER = ROOT / (
    "runtime/qualification/"
    "neuro_first_improvement_candidate_20261012_125609_722005"
)
CANDIDATE = FOLDER / "developer_chat_commands.candidate.py"
PATCH = FOLDER / "improvement.patch"
MANIFEST = FOLDER / "qualification_manifest.json"
REPORT_DIR = ROOT / "runtime/qualification/neuro_improvement_experiments"

EXPECTED_CANDIDATE = (
    "ebc85858755c0b7377fb6b2e7d6280e3e168c052c6eb74fb00d00f814e0d16f8"
)
EXPECTED_PATCH = (
    "e8b73896bbe1f8fe1a716adfa52a110c4a41ea85efa73249a4184798c8284e03"
)

TARGET = "_render_conversational_self_scan"
HELPER = "_collect_self_scan_findings"

TEST_NAMES = (
    "test_developer_conversational_self_scan.py",
    "test_developer_chat_commands.py",
    "test_developer_helper_extraction_scope.py",
    "test_neuro_improvement_history.py",
    "test_developer_role_guard.py",
    "test_developer_sensitive_filter_regression.py",
)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def fail(reason):
    print("EXPERIMENT_STATUS=BLOCKED")
    print("REASON=" + reason)
    print("PATCH_APPLIED=False")
    return 1

def functions(tree):
    return {
        node.name: node for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }

def branches(node):
    return sum(
        isinstance(n, (
            ast.If, ast.For, ast.While, ast.Try,
            ast.IfExp, ast.BoolOp, ast.Match,
        ))
        for n in ast.walk(node)
    )

BOOTSTRAP = r'''
import importlib
import pathlib
import sys
import types
import pytest

candidate = pathlib.Path(sys.argv[1])
paths = sys.argv[2:]
name = "backend.app.stacks.chat_public.developer_chat_commands"
package_name = "backend.app.stacks.chat_public"

original = importlib.import_module(name)
package = importlib.import_module(package_name)

replacement = types.ModuleType(name)
replacement.__dict__.update({
    "__name__": name,
    "__package__": package_name,
    "__file__": str(candidate),
    "__builtins__": __builtins__,
    "__spec__": original.__spec__,
})

exec(
    compile(candidate.read_bytes(), str(candidate), "exec"),
    replacement.__dict__,
)

sys.modules[name] = replacement
setattr(package, "developer_chat_commands", replacement)

assert replacement._render_conversational_self_scan is not (
    original._render_conversational_self_scan
)

print("TEST_SUBJECT=PINNED_CANDIDATE", flush=True)

raise SystemExit(pytest.main([
    "-q", "-p", "no:cacheprovider", *paths,
]))
'''

def main():
    print("=" * 68)
    print("NEUROVEST — BOUNDED IMPROVEMENT EXPERIMENT")
    print("=" * 68)

    if len(sys.argv) != 1:
        return fail("NO_DYNAMIC_ARGUMENTS_SUPPORTED")


    if (
        not LIVE_SOURCE.is_file()
        or not SOURCE.is_file()
        or sha(SOURCE) != EXPECTED_BASELINE_HASH
        or sha(LIVE_SOURCE) not in (
            EXPECTED_BASELINE_HASH,
            EXPECTED_INTEGRATED_HASH,
        )
    ):
        return fail("LIVE_SOURCE_OR_BASELINE_NOT_APPROVED")

    required = (SOURCE, CANDIDATE, PATCH, MANIFEST)
    if not all(p.is_file() for p in required):
        return fail("REQUIRED_ARTIFACT_MISSING")

    if sha(CANDIDATE) != EXPECTED_CANDIDATE:
        return fail("CANDIDATE_HASH_CHANGED")

    if sha(PATCH) != EXPECTED_PATCH:
        return fail("PATCH_HASH_CHANGED")

    try:
        manifest = json.loads(MANIFEST.read_text("utf-8"))
        if (
            manifest.get("source_sha256") != sha(SOURCE)
            or manifest.get("candidate_sha256") != EXPECTED_CANDIDATE
            or manifest.get("patch_sha256") != EXPECTED_PATCH
        ):
            return fail("MANIFEST_OR_SOURCE_CHANGED")

        original = ast.parse(SOURCE.read_bytes())
        candidate = ast.parse(CANDIDATE.read_bytes())
        compile(CANDIDATE.read_bytes(), str(CANDIDATE), "exec")
    except (ValueError, SyntaxError, OSError, TypeError) as exc:
        return fail("PREFLIGHT_" + type(exc).__name__)

    before = functions(original)
    after = functions(candidate)

    if TARGET not in before or TARGET not in after:
        return fail("TARGET_MISSING")

    if HELPER in before or HELPER not in after:
        return fail("HELPER_STRUCTURE_CHANGED")

    if set(after) != set(before) | {HELPER}:
        return fail("UNEXPECTED_FUNCTION_CHANGES")

    for name in before:
        if name != TARGET and (
            ast.dump(before[name]) != ast.dump(after[name])
        ):
            return fail("UNRELATED_FUNCTION_CHANGED")

    def other_statements(tree):
        return [
            ast.dump(node, include_attributes=False)
            for node in tree.body
            if not (
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name in (TARGET, HELPER)
            )
        ]

    if other_statements(original) != other_statements(candidate):
        return fail("UNRELATED_MODULE_CODE_CHANGED")

    old_branches = branches(before[TARGET])
    new_branches = branches(after[TARGET])
    helper_branches = branches(after[HELPER])

    if not (
        old_branches > new_branches
        and old_branches == new_branches + helper_branches
    ):
        return fail("BRANCH_CONTRACT_FAILED")

    tests = [
        ROOT / "backend/app/stacks/chat_public/tests" / name
        for name in TEST_NAMES
    ]
    if not all(p.is_file() for p in tests):
        return fail("TEST_FILE_MISSING")

    original_source_hash = sha(SOURCE)

    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

    print("CANDIDATE_HASH=VERIFIED")
    print("REVIEWED_PATCH_HASH=VERIFIED")
    print("SOURCE_MANIFEST_MATCH=PASS")
    print("SOURCE_SCOPE=PASS")
    print("TARGET_BRANCHES_BEFORE=", old_branches)
    print("TARGET_BRANCHES_AFTER=", new_branches)
    print("HELPER_BRANCHES=", helper_branches)
    print("RUNNING_CANDIDATE_TESTS=True", flush=True)

    try:
        result = subprocess.run(
            [
                str(ROOT / ".venv/bin/python"),
                "-B", "-c", BOOTSTRAP,
                str(CANDIDATE),
                *map(str, tests),
            ],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return fail("TEST_TIMEOUT")

    for line in result.stdout.splitlines():
        line = line.strip()
        if (
            "TEST_SUBJECT=" in line
            or "passed" in line
            or "failed" in line
            or "error" in line
        ):
            print("TEST_RESULT=", line[:200])

    unchanged = sha(SOURCE) == original_source_hash
    passed = (
        result.returncode == 0
        and "TEST_SUBJECT=PINNED_CANDIDATE" in result.stdout
        and unchanged
    )

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.chmod(0o700)

    stamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%S_%fZ"
    )
    report_path = REPORT_DIR / f"experiment_{stamp}.json"

    report = {
        "schema": "neurovest.bounded_improvement_experiment.v1",
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if passed else "FAILED",
        "target": TARGET,
        "candidate_sha256": EXPECTED_CANDIDATE,
        "patch_sha256": EXPECTED_PATCH,
        "source_sha256": original_source_hash,
        "source_unchanged": unchanged,
        "target_branch_nodes_before": old_branches,
        "target_branch_nodes_after": new_branches,
        "helper_branch_nodes": helper_branches,
        "test_exit_code": result.returncode,
        "candidate_substituted": (
            "TEST_SUBJECT=PINNED_CANDIDATE" in result.stdout
        ),
        "test_summary": [
            line.strip()[:200]
            for line in result.stdout.splitlines()
            if "passed" in line or "failed" in line
        ][-5:],
        "patch_applied": False,
        "developer_approval": False,
    }

    report_path.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    report_path.chmod(0o600)

    print("SOURCE_UNCHANGED=", unchanged)
    print("EVIDENCE_REPORT=", report_path)
    print("PATCH_APPLIED=False")
    print("DEVELOPER_APPROVAL=False")
    print("EXPERIMENT_STATUS=", report["status"])
    return 0 if passed else 1

if __name__ == "__main__":
    raise SystemExit(main())
