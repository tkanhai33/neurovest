"""Developer commands for the existing Neuro chat.

Explicit command syntax:
    /dev propose <allowed-source-file> :: <development-task>
    /dev show <proposal-id>

The existing authenticated developer gate must authorize entry.
No proposal application is performed by this module.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]

GENERATOR = (
    ROOT / "scripts/neuro_developer_patch_preview.py"
)

PROPOSALS = (
    ROOT / "runtime/developer_patch_proposals"
)

ALLOWED_SOURCE = (
    "backend/app/stacks/chat_public/"
    "developer_repository_inspection.py"
)

# NEUROVEST_PATCH_SCOPE_EXPANSION_V1
ADDITIONAL_SOURCE = (
    "backend/app/stacks/chat_public/"
    "developer_self_review.py"
)
ALLOWED_PATCH_SOURCES = (
    ALLOWED_SOURCE,
    ADDITIONAL_SOURCE,
)

PROPOSAL_ID = re.compile(
    r"^proposal_[0-9]{8}_[0-9]{6}_[0-9]+_[0-9]+$"
)

_generation_lock = threading.Lock()
_experiment_lock = threading.Lock()


def parse_developer_command(message: str):
    """Return an explicit developer command or None."""
    if not isinstance(message, str):
        return None

    text = message.strip()

    # NEUROVEST_EXPERIMENT_CHAT_V1
    experiment_text = re.sub(
        r"[^a-z0-9]+", " ", text.casefold()
    ).strip()

    if experiment_text in {
        "dev experiment",
        "mock up the proposed improvement and test it",
        "hey neuro mock up the proposed improvement and test it",
        "neuro mock up the proposed improvement and test it",
    }:
        return ("improvement_experiment",)

    # NEUROVEST_IMPROVEMENT_HISTORY_V1
    history_normalized = re.sub(
        r"[^a-z0-9]+", " ", text.casefold()
    ).strip()

    if history_normalized in {
        "hey neuro what have you learned about yourself",
        "neuro what have you learned about yourself",
        "hey neuro how is your self improvement coming along",
        "neuro how is your self improvement coming along",
        "hey neuro which problems keep appearing",
        "neuro which problems keep appearing",
        "hey neuro what should you improve first and why",
        "neuro what should you improve first and why",
        "hey neuro show me your improvement journal",
        "neuro show me your improvement journal",
    }:
        return ("improvement_history",)


    # NEUROVEST_CONVERSATIONAL_SELF_SCAN_V2
    normalized = re.sub(
        r"[^a-z0-9]+", " ", text.casefold()
    ).strip()

    if normalized in {
        "hey neuro what would help you improve",
        "neuro what would help you improve",
        "hey neuro how can you improve yourself",
        "neuro how can you improve yourself",
        "hey neuro what can you improve about yourself",
        "neuro what can you improve about yourself",
        "hey neuro scan yourself for improvements",
        "neuro scan yourself for improvements",
        "hey neuro what do you need to improve",
        "neuro what do you need to improve",
    }:
        return ("conversational_self_scan",)



    # NEUROVEST_REVIEW_TO_PROPOSAL_V1
    if text.startswith("/dev propose-review"):
        parts = text.split()

        if len(parts) != 4 or parts[:2] != [
            "/dev", "propose-review"
        ]:
            return (
                "error",
                "Use: /dev propose-review <module> <function>",
            )

        module_name, function_name = parts[2:]

        module_sources = {
            "developer_repository_inspection": ALLOWED_SOURCE,
            "developer_self_review": ADDITIONAL_SOURCE,
        }

        source = module_sources.get(module_name)

        if source not in ALLOWED_PATCH_SOURCES:
            return (
                "error",
                "Module is outside the approved patch scope.",
            )

        if not re.fullmatch(
            r"[A-Za-z_][A-Za-z0-9_]*",
            function_name,
        ):
            return ("error", "Invalid function name.")

        task = (
            "AUTO_REVIEW_DOCSTRING:"
            + function_name
            + " :: Add a docstring only to "
            + function_name
            + "; preserve all executable statements, "
            "signatures, and other functions."
        )

        return ("propose", source, task)

    if text.startswith("/dev propose "):
        body = text[len("/dev propose "):]

        if " :: " not in body:
            return (
                "error",
                "Use: /dev propose <file> :: <task>",
            )

        source, task = body.split(" :: ", 1)
        source = source.strip()
        task = task.strip()

        if source not in ALLOWED_PATCH_SOURCES:
            return (
                "error",
                "That source file is not enabled for "
                "developer patch generation yet.",
            )

        if not 12 <= len(task) <= 1500:
            return (
                "error",
                "The development task must contain "
                "12–1500 characters.",
            )

        return ("propose", source, task)

    # NEUROVEST_CHAT_PATCH_APPROVAL_V1
    if text.startswith("/dev apply"):
        parts = text.split()

        if (
            len(parts) != 4
            or parts[0] != "/dev"
            or parts[1] != "apply"
            or parts[3] != "--approve"
        ):
            return (
                "error",
                "Exact approval required: "
                "/dev apply <proposal-id> --approve",
            )

        proposal_id = parts[2]

        if not PROPOSAL_ID.fullmatch(proposal_id):
            return ("error", "Invalid proposal ID.")

        return ("apply", proposal_id)

    # NEUROVEST_SELF_REVIEW_ENGINE_V1
    if text.startswith("/dev review"):
        parts = text.split()

        if len(parts) != 3 or parts[:2] != ["/dev", "review"]:
            return (
                "error",
                "Use: /dev review <module-name>",
            )

        return ("review", parts[2])

    if text.startswith("/dev show "):
        proposal_id = text[len("/dev show "):].strip()

        if not PROPOSAL_ID.fullmatch(proposal_id):
            return (
                "error",
                "Invalid proposal ID.",
            )

        return ("show", proposal_id)

    return None


def _load_proposal(proposal_id: str) -> str:
    if not PROPOSAL_ID.fullmatch(proposal_id):
        return "Invalid proposal ID."

    directory = PROPOSALS / proposal_id

    if directory.is_symlink() or not directory.is_dir():
        return "Proposal not found."

    metadata_path = directory / "proposal.json"
    diff_path = directory / "change.diff"

    if any(
        not path.is_file() or path.is_symlink()
        for path in (metadata_path, diff_path)
    ):
        return "Proposal files are missing."

    if (
        metadata_path.stat().st_size > 16000
        or diff_path.stat().st_size > 32000
    ):
        return "Proposal exceeds preview limits."

    try:
        metadata = json.loads(
            metadata_path.read_text(encoding="utf-8")
        )
        diff = diff_path.read_text(encoding="utf-8")
    except (OSError, ValueError, UnicodeError):
        return "Unable to read the proposal."

    if (
        metadata.get("type") != "developer_patch_preview"
        or metadata.get("source_file") not in ALLOWED_PATCH_SOURCES
    ):
        return "Proposal is outside the enabled developer scope."

    explanation = str(
        metadata.get("explanation", "")
    )[:1200]

    return (
        "## Neuro Developer — Code Proposal\n\n"
        f"**Proposal:** `{proposal_id}`\n\n"
        f"**File:** `{metadata["source_file"]}`\n\n"
        f"**Model:** `{metadata.get('model', 'unknown')}`\n\n"
        f"**Explanation:** {explanation}\n\n"
        "### Proposed diff\n\n"
        "```diff\n"
        + diff[:12000]
        + "\n```\n\n"
        "**Status:** Preview only. No application source "
        "was changed. The proposal has not been "
        "functionally verified or approved."
    )



# NEUROVEST_CONVERSATIONAL_SELF_SCAN_V2
def _render_conversational_self_scan():
    """Read-only summary of allowlisted static review findings.

    This is a developer-command handler. The existing chat runtime
    must verify the authenticated developer principal before calling it.
    """
    from backend.app.stacks.chat_public.developer_self_review import (
        ALLOWED_MODULES,
        inventory_module,
    )

    import re

    def clean(value):
        return re.sub(
            r"\\s+", " ", str(value)
        ).replace("`", "'").strip()[:220]

    priorities = {
        "P0": 0,
        "P1": 1,
        "P2": 2,
        "P3": 3,
    }

    findings = []
    scanned = []
    unavailable = []

    for module in sorted(ALLOWED_MODULES):
        try:
            report = inventory_module(module)
        except (ValueError, OSError, SyntaxError) as exc:
            unavailable.append(
                module + " (" + type(exc).__name__ + ")"
            )
            continue

        scanned.append(module)

        for finding in report.get("findings", []):
            if not isinstance(finding, dict):
                continue

            priority = str(
                finding.get("priority")
                or finding.get("severity")
                or "P3"
            ).upper()

            if priority not in priorities:
                priority = "P3"

            findings.append({
                "module": module,
                "priority": priority,
                "function": clean(
                    finding.get("function")
                    or finding.get("function_name")
                    or finding.get("name")
                    or "module"
                ),
                "kind": clean(
                    finding.get("type")
                    or finding.get("kind")
                    or finding.get("category")
                    or "static finding"
                ),
                "evidence": clean(
                    finding.get("evidence")
                    or finding.get("detail")
                    or finding.get("description")
                    or "Identified by static inspection"
                ),
                "recommendation": clean(
                    finding.get("recommendation")
                    or finding.get("suggestion")
                    or "Review the code and add focused tests"
                ),
            })

    findings.sort(
        key=lambda f: (
            priorities[f["priority"]],
            f["module"],
            f["function"],
            f["kind"],
        )
    )

    lines = [
        "## Neuro Developer — Self-Improvement Scan",
        "",
        "I've scanned the parts of myself that I'm "
        "authorized to inspect.",
        "",
        "**Access:** Authenticated developer only.",
        "**Method:** Read-only AST analysis.",
        "**Modules scanned:** "
        + str(len(scanned))
        + " of "
        + str(len(ALLOWED_MODULES)),
        "",
        "### Where I need improvement",
        "",
    ]

    chosen = []
    seen = set()

    for finding in findings:
        key = (
            finding["module"],
            finding["function"],
            finding["kind"],
        )
        if key in seen:
            continue
        seen.add(key)
        chosen.append(finding)
        if len(chosen) >= 4:
            break

    if not chosen:
        lines.append(
            "No actionable static findings were returned. "
            "This does not establish that the code is defect-free."
        )

    for index, finding in enumerate(chosen, 1):
        lines.extend([
            str(index) + ". **"
            + clean(finding["module"])
            + " / "
            + finding["function"]
            + "** (" + finding["priority"] + ")",
            "   - Finding: " + finding["kind"],
            "   - Evidence: " + finding["evidence"],
            "   - Improvement: " + finding["recommendation"],
            "",
        ])

    lines.extend(["", "### My recommendation", ""])

    if chosen:
        top = chosen[0]

        lines.extend([
            "I recommend reviewing **"
            + clean(top["module"])
            + " / "
            + top["function"]
            + "** first.",
            "",
            "**Why:** " + top["evidence"],
            "",
            "**Suggested change:** " + top["recommendation"],
            "",
            "**Expected benefit:** Addressing this finding "
            "may improve maintainability, clarity, or reliability. "
            "The actual benefit must be confirmed with tests.",
            "",
            "**Risk:** A structural change can introduce "
            "regressions. Any proposal requires diff review, "
            "explicit approval, focused tests, and rollback.",
        ])
    else:
        lines.append(
            "No change is recommended without supported findings."
        )

    if unavailable:
        lines.extend([
            "",
            "### Scan limitations",
            "",
            "Unavailable modules: " + ", ".join(unavailable),
        ])

    lines.extend([
        "",
        "This report covers only approved self-review modules. "
        "No code was changed, approved, or deployed.",
    ])

    return "\n".join(lines)


def handle_developer_command(command) -> str:
    """Execute only a recognized, authorized preview command.

    The caller is responsible for enforcing authenticated
    developer access before invoking this function.
    """
    action = command[0]

    # NEUROVEST_EXPERIMENT_CHAT_V1
    if action == "improvement_experiment":
        if len(command) != 1:
            return "Invalid improvement experiment command."

        runner = ROOT / "scripts/neuro_improvement_experiment.py"

        if not runner.is_file():
            return "Improvement experiment runner unavailable."

        if not _experiment_lock.acquire(blocking=False):
            return "An improvement experiment is already running."

        try:
            environment = os.environ.copy()
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            environment["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

            try:
                result = subprocess.run(
                    [sys.executable, "-B", str(runner)],
                    cwd=ROOT,
                    env=environment,
                    capture_output=True,
                    text=True,
                    timeout=150,
                    check=False,
                )
            except (OSError, subprocess.TimeoutExpired):
                return (
                    "Neuro improvement experiment could not complete. "
                    "No patch was applied."
                )

            if result.returncode != 0 or not re.search(
                r"(?m)^EXPERIMENT_STATUS=\s*PASS\s*$",
                result.stdout,
            ):
                return (
                    "Neuro improvement experiment did not qualify. "
                    "No patch was applied. Check the experiment "
                    "qualification logs."
                )

            path_match = re.search(
                r"(?m)^EVIDENCE_REPORT=\s*(.+?)\s*$",
                result.stdout,
            )

            if path_match is None:
                return "Experiment evidence report missing."

            report_dir = (
                ROOT / "runtime/qualification/"
                "neuro_improvement_experiments"
            ).resolve()

            report_file = Path(path_match.group(1)).resolve()

            if (
                report_file.parent != report_dir
                or not report_file.is_file()
            ):
                return "Experiment evidence location invalid."

            try:
                evidence = json.loads(
                    report_file.read_text("utf-8")
                )
            except (OSError, ValueError):
                return "Experiment evidence could not be verified."

            if not (
                evidence.get("status") == "PASS"
                and evidence.get("candidate_substituted") is True
                and evidence.get("source_unchanged") is True
                and evidence.get("test_exit_code") == 0
                and evidence.get("patch_applied") is False
                and evidence.get("developer_approval") is False
            ):
                return "Experiment evidence verification failed."

            summary = evidence.get("test_summary") or []
            test_summary = next(
                (
                    str(value)[:160]
                    for value in summary
                    if "passed" in str(value)
                ),
                "Focused tests completed",
            )

            return "\n".join([
                "## Neuro Developer — Improvement Experiment",
                "",
                "**Result:** PASS — real candidate tests executed.",
                "**Target:** `_render_conversational_self_scan`",
                "**Regression tests:** " + test_summary,
                "**Target branch nodes:** "
                    + str(evidence["target_branch_nodes_before"])
                    + " → "
                    + str(evidence["target_branch_nodes_after"]),
                "**Extracted helper branch nodes:** "
                    + str(evidence["helper_branch_nodes"]),
                "**Evidence:** `" + report_file.name + "`",
                "",
                "This experiment tests the previously qualified, "
                "pinned candidate. It does not generate arbitrary "
                "new patches.",
                "",
                "**Safety:** No patch applied, no developer "
                "approval granted, no trading action performed.",
            ])
        finally:
            _experiment_lock.release()

    # NEUROVEST_IMPROVEMENT_HISTORY_V1
    if action == "improvement_history":
        if len(command) != 1:
            return "Invalid improvement history command."

        root = Path(__file__).resolve().parents[4]
        reader = root / "scripts/neuro_improvement_history.py"

        try:
            result = subprocess.run(
                [
                    str(root / '.venv/bin/python'),
                    str(reader),
                ],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            return (
                "Neuro improvement journal is currently "
                "unavailable. No changes were made."
            )

        if result.returncode:
            return (
                "Neuro improvement journal could not "
                "be read. No changes were made."
            )

        return result.stdout[:12000]


    # NEUROVEST_CONVERSATIONAL_SELF_SCAN_V2
    if action == "conversational_self_scan":
        if len(command) != 1:
            return "Invalid developer self-scan command."
        return _render_conversational_self_scan()


    if action == "error":
        return command[1]

    if action == "show":
        return _load_proposal(command[1])

    if action == "review":
        from backend.app.stacks.chat_public.developer_self_review import (
            render_review,
        )

        if len(command) != 2:
            return "Invalid self-review command."

        return render_review(command[1])


    if action == "apply":
        if len(command) != 2:
            return "Invalid patch approval command."

        proposal_id = command[1]

        if (
            not isinstance(proposal_id, str)
            or not PROPOSAL_ID.fullmatch(proposal_id)
        ):
            return "Invalid proposal ID."

        directory = PROPOSALS / proposal_id

        if directory.is_symlink() or not directory.is_dir():
            return "Proposal not found."

        metadata_file = directory / "proposal.json"
        diff_file = directory / "change.diff"

        if any(
            path.is_symlink() or not path.is_file()
            for path in (metadata_file, diff_file)
        ):
            return "Invalid or missing proposal files."

        try:
            if (
                metadata_file.stat().st_size > 16000
                or diff_file.stat().st_size > 32000
            ):
                return "Proposal exceeds approval limits."

            metadata = json.loads(
                metadata_file.read_text(encoding="utf-8")
            )

            if (
                not isinstance(metadata, dict)
                or metadata.get("type") != "developer_patch_preview"
                or metadata.get("source_file") not in ALLOWED_PATCH_SOURCES
            ):
                return "Proposal is outside the permitted source scope."

        except (OSError, ValueError, TypeError, UnicodeError):
            return "Could not validate proposal metadata."

        # Uses the same lock as proposal generation, preventing
        # generation and application from overlapping in this worker.
        if not _generation_lock.acquire(blocking=False):
            return "Another developer patch operation is in progress."

        try:
            environment = os.environ.copy()
            environment["PYTHONDONTWRITEBYTECODE"] = "1"

            try:
                result = subprocess.run(
                    [
                        sys.executable,
                        str(
                            ROOT
                            / "scripts/neuro_developer_patch_apply.py"
                        ),
                        "--proposal",
                        str(directory),
                        "--approve",
                    ],
                    cwd=ROOT,
                    env=environment,
                    capture_output=True,
                    text=True,
                    timeout=150,
                    check=False,
                )

            except subprocess.TimeoutExpired:
                return (
                    "Developer patch application exceeded its time limit. "
                    "The application state must be inspected before "
                    "retrying; automatic success is not assumed."
                )

            output = (
                result.stdout[-4500:]
                + (
                    "\n" + result.stderr[-700:]
                    if result.stderr else ""
                )
            )

            if result.returncode != 0:
                return (
                    "## Neuro Developer — Patch Application Failed\n\n"
                    f"**Proposal:** `{proposal_id}`\n\n"
                    "The patch tool reported failure. "
                    "Inspect the recorded outcome before retrying.\n\n"
                    "```text\n"
                    + output
                    + "\n```"
                )

            # Never infer success merely from the exit code.
            if (
                "PATCH_APPLIED=True" not in result.stdout
                or "FOCUSED_TEST" not in result.stdout
            ):
                return (
                    "## Neuro Developer — Outcome Needs Inspection\n\n"
                    "The patch tool exited successfully, but its "
                    "application/test confirmation was incomplete.\n\n"
                    "```text\n"
                    + output
                    + "\n```"
                )

            return (
                "## Neuro Developer — Approved Patch Applied\n\n"
                f"**Proposal:** `{proposal_id}`\n\n"
                f"**Source:** `{metadata['source_file']}`\n\n"
                "The existing patch tool reports that the patch was "
                "applied and focused tests were executed.\n\n"
                "```text\n"
                + output
                + "\n```\n\n"
                "This does not restart or deploy the running backend."
            )

        finally:
            _generation_lock.release()


    if action != "propose":
        return "Unsupported developer command."

    _, source, task = command

    if source not in ALLOWED_PATCH_SOURCES:
        return "Developer source is not allowed."

    if not _generation_lock.acquire(blocking=False):
        return (
            "A developer code proposal is already generating."
        )

    try:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(GENERATOR),
                    "--file",
                    source,
                    "--task",
                    task,
                ],
                cwd=ROOT,
                env=environment,
                capture_output=True,
                text=True,
                timeout=190,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return (
                "The local coding model timed out. "
                "No application code was changed."
            )

        if result.returncode != 0:
            return (
                "Local code proposal generation failed.\n\n"
                "```text\n"
                + result.stdout[-900:]
                + "\n```\n\n"
                "No application code was changed."
            )

        match = re.search(
            r"(?m)^PROPOSAL_DIR=\s*(.+?)\s*$",
            result.stdout,
        )

        if not match:
            return (
                "The patch generator completed, but its "
                "proposal directory was not reported."
            )

        directory = Path(match.group(1)).resolve()

        if directory.parent != PROPOSALS.resolve():
            return "Invalid generated proposal location."

        if not PROPOSAL_ID.fullmatch(directory.name):
            return "Invalid generated proposal identifier."

        return _load_proposal(directory.name)

    finally:
        _generation_lock.release()
