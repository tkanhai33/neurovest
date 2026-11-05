from __future__ import annotations

import ast
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
STACKS = ROOT / "backend/app/stacks"
RELEASES = ROOT / "runtime/releases"

VERSION = "NEUROVEST_DIAGNOSTICS_3F"

MAX_STACKS = 64
MAX_FILES_PER_STACK = 1000
MAX_RELEASES = 60
MAX_LOG_BYTES = 200_000

FAMILIES = {
    "natural_research": "neuro_natural_chat_3A_",
    "model_tool_router": "neuro_intelligence_3B_",
    "general_response": "neuro_intelligence_3C_",
    "completion_guard": "neuro_completion_3DR1_",
    "relevance_guard": "neuro_relevance_3DR2_",
    "developer_inventory": "neuro_intelligence_3E_",
    "developer_authorization": "neuro_developer_3ER1_",
    "developer_routing": "neuro_developer_3ER3_",
    "developer_execution_trace": "neuro_developer_3ER4_",
}

PASS_PATTERN = re.compile(
    r"(?m)^(?:TEST_RESULT|INSTALL_RESULT)=PASS\s*$"
)
FAIL_PATTERN = re.compile(
    r"(?m)^(?:TEST_RESULT|INSTALL_RESULT)=FAIL\s*$"
)


def _parse_status(path: Path) -> str:
    try:
        if not path.is_file():
            return "missing"
        if path.stat().st_size > 1_000_000:
            return "not_inspected_size_limit"
        ast.parse(path.read_text(encoding="utf-8"))
        return "syntax_valid"
    except (OSError, UnicodeError, SyntaxError, ValueError):
        return "invalid_or_unreadable"


def discover_capabilities() -> dict:
    """
    Discover stack-level source structure without importing
    modules, executing application code, or reading secrets.
    """
    results = {}

    if not STACKS.is_dir():
        return results

    try:
        directories = sorted(
            p for p in STACKS.iterdir()
            if p.is_dir()
            and not p.is_symlink()
            and not p.name.startswith(".")
        )[:MAX_STACKS]
    except OSError:
        return results

    for stack in directories:
        try:
            files = sorted(
                p for p in stack.rglob("*.py")
                if p.is_file()
                and not p.is_symlink()
            )[:MAX_FILES_PER_STACK]
        except OSError:
            results[stack.name] = {
                "source_files": 0,
                "test_files": 0,
                "sampled_syntax_valid": 0,
                "inspection": "unavailable",
            }
            continue

        test_files = [
            p for p in files
            if p.name.startswith("test_")
            or "tests" in p.relative_to(stack).parts
        ]

        sample = [
            p for p in files
            if p not in test_files
        ][:8]

        results[stack.name] = {
            "source_files": len(files),
            "test_files": len(test_files),
            "sampled_syntax_valid": sum(
                _parse_status(p) == "syntax_valid"
                for p in sample
            ),
            "sample_size": len(sample),
            "inspection": "bounded_source_discovery",
        }

    return results


def inspect_qualifications() -> dict:
    """
    Inspect only known release families and exact pass/fail
    markers. Never return raw logs, tokens, paths or account
    data to the model.
    """
    results = {}

    if not RELEASES.is_dir():
        return {
            family: "release_history_unavailable"
            for family in FAMILIES
        }

    try:
        directories = [
            p for p in RELEASES.iterdir()
            if p.is_dir()
            and not p.is_symlink()
        ]
    except OSError:
        directories = []

    for family, prefix in FAMILIES.items():
        matches = sorted(
            (p for p in directories
             if p.name.startswith(prefix)),
            key=lambda p: p.name,
            reverse=True,
        )[:MAX_RELEASES]

        if not matches:
            results[family] = "no_matching_release"
            continue

        latest = matches[0]
        test_log = latest / "evidence/tests.log"
        install_log = latest / "evidence/install.log"

        status = "release_directory_only"

        for path in (test_log, install_log):
            try:
                if not path.is_file():
                    continue

                if path.stat().st_size > MAX_LOG_BYTES:
                    status = "log_exceeds_inspection_limit"
                    continue

                text = path.read_text(errors="replace")

                if FAIL_PATTERN.search(text):
                    status = "recorded_failure"
                    break

                if PASS_PATTERN.search(text):
                    status = (
                        "focused_test_pass_recorded"
                        if path == test_log
                        else "install_pass_recorded"
                    )
                    break
            except OSError:
                status = "log_unreadable"

        results[family] = status

    return results


def inspect_runtime_signals() -> dict:
    """
    Bounded static observations only. No production journal,
    database, user data or environment-variable inspection.
    """
    chat = STACKS / "chat_public"

    targets = {
        "chat_runtime": chat / "chat_runtime.py",
        "retrieval_relevance": (
            chat / "answer_relevance_3dr2.py"
        ),
        "completion_guard": (
            chat / "ollama_completion_guard_3dr1.py"
        ),
        "developer_authorization": (
            chat / "developer_authorization_3er1.py"
        ),
        "developer_routing": (
            chat / "developer_awareness_route_3er3.py"
        ),
        "execution_trace": (
            chat / "developer_execution_trace_3er4.py"
        ),
        "financial_bridge": (
            chat / "financial_analysis_chat_bridge.py"
        ),
    }

    return {
        name: _parse_status(path)
        for name, path in targets.items()
    }


def build_report() -> str:
    capabilities = discover_capabilities()
    qualifications = inspect_qualifications()
    runtime = inspect_runtime_signals()

    now = datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M UTC"
    )

    total_sources = sum(
        x["source_files"]
        for x in capabilities.values()
    )

    total_tests = sum(
        x["test_files"]
        for x in capabilities.values()
    )

    statuses = Counter(qualifications.values())

    lines = [
        "# NeuroVest intelligence improvement assessment",
        "",
        f"Assessment generated: {now}",
        "",
        "## What I can verify",
        "",
        f"- Discovered stack directories: {len(capabilities)}",
        f"- Python files counted in bounded scan: {total_sources}",
        f"- Test-related Python files counted: {total_tests}",
        "- Source inspection is not runtime qualification.",
        "- Release pass markers are historical observations, "
        "not proof of current production behavior.",
        "",
        "## Architecture capability inventory",
        "",
    ]

    if not capabilities:
        lines.append(
            "- Architecture discovery unavailable."
        )

    for stack, data in sorted(capabilities.items()):
        lines.append(
            f"- {stack}: "
            f"{data['source_files']} Python files, "
            f"{data['test_files']} test-related files; "
            f"syntax-valid samples "
            f"{data['sampled_syntax_valid']}/"
            f"{data.get('sample_size', 0)}"
        )

    lines.extend([
        "",
        "## Release qualification signals",
        "",
    ])

    for family, status in qualifications.items():
        lines.append(f"- {family}: {status}")

    lines.extend([
        "",
        "## Runtime integration source checks",
        "",
    ])

    for name, status in runtime.items():
        lines.append(f"- {name}: {status}")

    lines.extend([
        "",
        "## Prioritized improvements",
        "",
        "### P1 — General-answer relevance",
        "Evidence: relevance-guard source and release "
        "qualification status are listed above. "
        "Historical live-chat evaluation identified "
        "unrelated manual-transmission answers. "
        "That observation requires fresh reproduction.",
        "Next validation: run a fixed multi-domain question "
        "set through authenticated chat, compare requested "
        "topics with returned topics, and measure failures.",
        "",
        "### P1 — Response completeness",
        "Evidence: completion-guard presence and recorded "
        "qualification status are listed above. "
        "Previous live examples ended with unfinished "
        "sentences. This report does not measure current "
        "truncation rates.",
        "Next validation: compare local model completion "
        "reasons, API response length, persisted message "
        "length, and frontend display for the same turns.",
        "",
        "### P2 — Retrieval provenance and grounding",
        "Evidence: architecture inventory and known "
        "research integration modules. "
        "This inventory does not prove retrieval relevance.",
        "Next validation: record sanitized evidence-source "
        "identifiers, topic match adjudication, freshness, "
        "and citation support without exposing user data.",
        "",
        "### P2 — Conversational state and tool selection",
        "Evidence: natural research and model-tool routing "
        "release statuses above.",
        "Next validation: qualify follow-up questions, "
        "subject continuity, owner isolation, and safe "
        "fallback behavior across multi-turn conversations.",
        "",
        "### P2 — Developer self-assessment expansion",
        "Evidence: this assessment inventories source "
        "and historical qualification markers, but does "
        "not run diagnostic probes on demand.",
        "Next validation: expose approved read-only "
        "diagnostic actions with explicit scope, evidence "
        "timestamps, and developer-only authorization.",
        "",
        "## Qualification coverage",
        "",
        f"- Known release families inspected: "
        f"{len(qualifications)}",
        f"- Families with recorded focused passes: "
        f"{statuses['focused_test_pass_recorded']}",
        f"- Families with recorded failures: "
        f"{statuses['recorded_failure']}",
        "- End-to-end production accuracy: not measured "
        "by this report.",
        "- Current response quality: not independently "
        "measured by this report.",
        "",
        "## Safety and authority",
        "",
        "- This is a read-only developer evidence report.",
        "- Source files were inspected but not executed.",
        "- No self-modification or deployment was performed.",
        "- No user account contents or raw logs were read.",
        "- No database writes, billing actions, system-mode "
        "transitions, or broker orders were authorized.",
        "",
        "Recommended engineering action: qualify general "
        "answer relevance and completeness against the "
        "actual authenticated chat path before promoting "
        "either capability to production-qualified.",
    ])

    # NEUROVEST_MODEL_QUALIFICATION_3G
    # Read sanitized results from completed local-model probes.
    # Never execute inference inside a user's chat request.
    from backend.app.stacks.chat_public.model_qualification_3g import (
        report_section,
    )
    lines.extend([""] + report_section())

    return "\n".join(lines)
