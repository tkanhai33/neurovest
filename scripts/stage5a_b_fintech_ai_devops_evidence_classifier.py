#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable


ROOT = Path(".").resolve()

EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".next",
    "dist",
    "build",
    "coverage",
    "htmlcov",
    "archive",
    "backups",
    "architecture_backup",
    "quarantine_artifacts",
}

RUNTIME_EXCLUDED = {
    "runtime",
}

TEXT_SUFFIXES = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".json",
    ".toml",
    ".ini",
    ".cfg",
    ".yaml",
    ".yml",
    ".md",
    ".txt",
    ".sh",
    ".sql",
}

MAX_FILE_BYTES = 2_000_000


@dataclass
class ControlResult:
    control_id: str
    domain: str
    control: str
    status: str
    readiness_gate: str
    evidence: list[str]
    gaps: list[str]
    next_action: str


def run_command(
    command: list[str],
    *,
    timeout: int = 30,
) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )

        output = (
            completed.stdout
            + completed.stderr
        ).strip()

        return completed.returncode, output

    except Exception as exc:
        return (
            1,
            f"{type(exc).__name__}: {exc}",
        )


def iter_source_files(
    *,
    include_runtime: bool = False,
) -> Iterable[Path]:
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue

        relative = path.relative_to(ROOT)

        if any(
            part in EXCLUDED_PARTS
            for part in relative.parts
        ):
            continue

        if (
            not include_runtime
            and any(
                part in RUNTIME_EXCLUDED
                for part in relative.parts
            )
        ):
            continue

        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue

        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                continue
        except OSError:
            continue

        yield path


SOURCE_FILES = list(
    iter_source_files()
)


def relative(path: Path) -> str:
    try:
        return str(
            path.relative_to(ROOT)
        )
    except ValueError:
        return str(path)


def existing_paths(
    candidates: Iterable[str],
) -> list[str]:
    found: list[str] = []

    for candidate in candidates:
        path = ROOT / candidate

        if path.exists():
            found.append(candidate)

    return found


def filenames_matching(
    patterns: Iterable[str],
    *,
    limit: int = 30,
) -> list[str]:
    compiled = [
        re.compile(
            pattern,
            re.IGNORECASE,
        )
        for pattern in patterns
    ]

    found: list[str] = []

    for path in SOURCE_FILES:
        target = relative(path)

        if any(
            pattern.search(target)
            for pattern in compiled
        ):
            found.append(target)

            if len(found) >= limit:
                break

    return found


def content_matching(
    patterns: Iterable[str],
    *,
    path_patterns: Iterable[str] | None = None,
    limit: int = 30,
) -> list[str]:
    compiled = [
        re.compile(
            pattern,
            re.IGNORECASE,
        )
        for pattern in patterns
    ]

    compiled_paths = [
        re.compile(
            pattern,
            re.IGNORECASE,
        )
        for pattern in (
            path_patterns or []
        )
    ]

    matches: list[str] = []

    for path in SOURCE_FILES:
        target = relative(path)

        if compiled_paths and not any(
            pattern.search(target)
            for pattern in compiled_paths
        ):
            continue

        try:
            text = path.read_text(
                encoding="utf-8",
                errors="replace",
            )
        except OSError:
            continue

        for number, line in enumerate(
            text.splitlines(),
            start=1,
        ):
            if any(
                pattern.search(line)
                for pattern in compiled
            ):
                sanitized = line.strip()

                if len(sanitized) > 180:
                    sanitized = (
                        sanitized[:177]
                        + "..."
                    )

                matches.append(
                    f"{target}:{number}: "
                    f"{sanitized}"
                )

                if len(matches) >= limit:
                    return matches

    return matches


def count_test_files() -> int:
    return sum(
        1
        for path in SOURCE_FILES
        if (
            path.name.startswith("test_")
            or path.name.endswith("_test.py")
            or ".spec." in path.name
            or ".test." in path.name
        )
    )


def control(
    control_id: str,
    domain: str,
    name: str,
    *,
    pass_evidence: list[str],
    partial_evidence: list[str] | None = None,
    required_gap: str,
    readiness_gate: str,
    next_action: str,
    blocked: bool = False,
) -> ControlResult:
    partial_evidence = (
        partial_evidence or []
    )

    evidence = list(
        dict.fromkeys(
            pass_evidence
            + partial_evidence
        )
    )

    if blocked:
        status = (
            "BLOCKED — REQUIRES "
            "RUNTIME QUALIFICATION"
        )

        gaps = [required_gap]

    elif pass_evidence:
        status = "PASS"
        gaps = []

    elif partial_evidence:
        status = "PARTIAL"
        gaps = [required_gap]

    else:
        status = "MISSING"
        gaps = [required_gap]

    return ControlResult(
        control_id=control_id,
        domain=domain,
        control=name,
        status=status,
        readiness_gate=readiness_gate,
        evidence=evidence,
        gaps=gaps,
        next_action=next_action,
    )


results: list[ControlResult] = []


# ==========================================================
# REPOSITORY AND SOURCE CONTROL
# ==========================================================

workflow_files = existing_paths(
    [
        ".github/workflows/architecture_ci.yml",
        ".github/workflows/ci.yml",
        ".github/workflows/test.yml",
        ".github/dependabot.yml",
        ".github/CODEOWNERS",
    ]
)

results.append(
    control(
        "DEVOPS-001",
        "Repository Governance",
        "Canonical CI workflow exists",
        pass_evidence=[
            path
            for path in workflow_files
            if path.startswith(
                ".github/workflows/"
            )
        ],
        required_gap=(
            "No canonical project CI workflow "
            "was located."
        ),
        readiness_gate="Controlled Early User",
        next_action=(
            "Qualify the existing workflow for "
            "backend, frontend, security, and "
            "architecture gates."
        ),
    )
)

branch_protection_evidence = existing_paths(
    [
        ".github/CODEOWNERS",
        ".github/pull_request_template.md",
        ".github/PULL_REQUEST_TEMPLATE.md",
        ".github/SECURITY.md",
    ]
)

results.append(
    control(
        "DEVOPS-002",
        "Repository Governance",
        "Review and branch-governance evidence",
        pass_evidence=branch_protection_evidence,
        required_gap=(
            "Repository-local review ownership, "
            "pull-request policy, or security "
            "reporting evidence is incomplete."
        ),
        readiness_gate="Production",
        next_action=(
            "Add and externally qualify branch "
            "protection, required reviews, and "
            "CODEOWNERS."
        ),
    )
)


# ==========================================================
# BUILD AND DEPLOYMENT
# ==========================================================

dependency_files = existing_paths(
    [
        "pyproject.toml",
        "requirements.txt",
        "requirements.lock",
        "poetry.lock",
        "uv.lock",
        "Pipfile.lock",
        "frontend/package.json",
        "frontend/package-lock.json",
        "frontend/pnpm-lock.yaml",
        "frontend/yarn.lock",
    ]
)

python_lock = [
    path
    for path in dependency_files
    if path in {
        "requirements.lock",
        "poetry.lock",
        "uv.lock",
        "Pipfile.lock",
    }
]

frontend_lock = [
    path
    for path in dependency_files
    if path.endswith(
        (
            "package-lock.json",
            "pnpm-lock.yaml",
            "yarn.lock",
        )
    )
]

results.append(
    control(
        "DEVOPS-003",
        "Build Reproducibility",
        "Dependency manifests and lock files",
        pass_evidence=(
            python_lock
            + frontend_lock
        ),
        partial_evidence=dependency_files,
        required_gap=(
            "Both backend and frontend dependencies "
            "must be reproducibly pinned and "
            "verified in CI."
        ),
        readiness_gate="Controlled Early User",
        next_action=(
            "Freeze backend dependencies and verify "
            "lock-file installation in CI."
        ),
    )
)

container_files = existing_paths(
    [
        "Dockerfile",
        "backend/Dockerfile",
        "frontend/Dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        "compose.yml",
        "compose.yaml",
    ]
)

results.append(
    control(
        "DEVOPS-004",
        "Deployment",
        "Container and local deployment definitions",
        pass_evidence=[
            path
            for path in container_files
            if "Dockerfile" in path
        ],
        partial_evidence=container_files,
        required_gap=(
            "Container build definitions are "
            "missing or incomplete for one or more "
            "runtime components."
        ),
        readiness_gate="Controlled Early User",
        next_action=(
            "Qualify immutable backend and frontend "
            "images with health checks and "
            "non-root execution."
        ),
    )
)

health_evidence = content_matching(
    [
        r"\bhealth(check)?\b",
        r"\breadiness\b",
        r"\bliveness\b",
        r"/health",
        r"/ready",
    ],
    path_patterns=[
        r"backend/",
        r"docker",
        r"github/workflows",
    ],
)

results.append(
    control(
        "DEVOPS-005",
        "Deployment",
        "Liveness and readiness contracts",
        pass_evidence=health_evidence,
        required_gap=(
            "Deployment-grade liveness and "
            "readiness probes were not proven."
        ),
        readiness_gate="Controlled Early User",
        next_action=(
            "Create explicit dependency-aware "
            "health, readiness, and startup probes."
        ),
    )
)

rollback_evidence = filenames_matching(
    [
        r"rollback",
        r"restore",
        r"disaster",
        r"backup",
        r"runbook",
    ]
)

results.append(
    control(
        "DEVOPS-006",
        "Deployment",
        "Deployment rollback and recovery runbook",
        pass_evidence=rollback_evidence,
        required_gap=(
            "A qualified deployment rollback "
            "procedure was not located."
        ),
        readiness_gate="Production",
        next_action=(
            "Document and exercise application, "
            "database, and configuration rollback."
        ),
    )
)


# ==========================================================
# SECURITY AND SUPPLY CHAIN
# ==========================================================

secret_controls = filenames_matching(
    [
        r"secret",
        r"password",
        r"jwt",
        r"credential",
        r"revocation",
    ]
)

results.append(
    control(
        "SEC-001",
        "Security",
        "Authentication and secret boundaries",
        pass_evidence=secret_controls,
        required_gap=(
            "Authentication, secret handling, and "
            "revocation boundaries are incomplete."
        ),
        readiness_gate="Controlled Early User",
        next_action=(
            "Retain the qualified identity-auth "
            "boundary and add automated secret "
            "scanning."
        ),
    )
)

security_ci = content_matching(
    [
        r"pip-audit",
        r"safety check",
        r"bandit",
        r"semgrep",
        r"trivy",
        r"grype",
        r"syft",
        r"npm audit",
        r"dependency-check",
        r"codeql",
        r"gitleaks",
        r"detect-secrets",
    ],
    path_patterns=[
        r"\.github/workflows/",
        r"scripts/",
        r"pyproject",
        r"package\.json",
    ],
)

results.append(
    control(
        "SEC-002",
        "Supply Chain Security",
        "Automated dependency and source scanning",
        pass_evidence=security_ci,
        required_gap=(
            "Automated SAST, dependency, container, "
            "and secret scanning is not fully "
            "evidenced."
        ),
        readiness_gate="Controlled Early User",
        next_action=(
            "Add fail-closed CI gates for SAST, "
            "dependency vulnerabilities, secrets, "
            "and container scanning."
        ),
    )
)

sbom_evidence = content_matching(
    [
        r"\bsbom\b",
        r"cyclonedx",
        r"spdx",
        r"\bsyft\b",
    ],
    path_patterns=[
        r"\.github/",
        r"scripts/",
        r"docker",
        r"pyproject",
        r"package",
    ],
)

results.append(
    control(
        "SEC-003",
        "Supply Chain Security",
        "Software bill of materials",
        pass_evidence=sbom_evidence,
        required_gap=(
            "No repeatable SBOM generation and "
            "retention process was proven."
        ),
        readiness_gate="Production",
        next_action=(
            "Generate backend, frontend, and "
            "container SBOMs during release builds."
        ),
    )
)

rate_limit_evidence = content_matching(
    [
        r"rate.?limit",
        r"throttl",
        r"semaphore",
        r"request.?limit",
        r"payload.?limit",
    ],
    path_patterns=[
        r"backend/app/",
    ],
)

results.append(
    control(
        "SEC-004",
        "Application Security",
        "Abuse, rate, and resource controls",
        pass_evidence=rate_limit_evidence,
        required_gap=(
            "Rate limiting and resource-exhaustion "
            "controls are not fully proven across "
            "public endpoints."
        ),
        readiness_gate="Controlled Early User",
        next_action=(
            "Qualify limits by route class, identity, "
            "IP, payload size, and expensive AI "
            "operation."
        ),
    )
)


# ==========================================================
# DATABASE, BACKUPS, AND DATA GOVERNANCE
# ==========================================================

migration_evidence = existing_paths(
    [
        "alembic.ini",
        "alembic",
    ]
) + filenames_matching(
    [
        r"migration",
        r"alembic",
    ]
)

results.append(
    control(
        "DATA-001",
        "Database",
        "Versioned schema migrations",
        pass_evidence=migration_evidence,
        required_gap=(
            "Versioned, repeatable schema migration "
            "evidence was not found."
        ),
        readiness_gate="Controlled Early User",
        next_action=(
            "Qualify upgrade, downgrade, transaction, "
            "and failed-migration recovery."
        ),
    )
)

backup_evidence = filenames_matching(
    [
        r"backup",
        r"restore",
        r"recovery",
        r"snapshot",
    ]
)

results.append(
    control(
        "DATA-002",
        "Resilience",
        "Database backup and restore",
        pass_evidence=backup_evidence,
        required_gap=(
            "A tested database backup and restore "
            "contract was not proven."
        ),
        readiness_gate="Production",
        next_action=(
            "Define RPO/RTO and execute a clean "
            "restore qualification."
        ),
    )
)

retention_evidence = content_matching(
    [
        r"retention",
        r"purge",
        r"delete_expired",
        r"cleanup",
        r"data lifecycle",
    ],
    path_patterns=[
        r"backend/",
        r"handoff/",
        r".*\.md$",
    ],
)

results.append(
    control(
        "DATA-003",
        "Data Governance",
        "Retention and deletion controls",
        pass_evidence=retention_evidence,
        required_gap=(
            "System-wide retention and deletion "
            "requirements are not fully defined."
        ),
        readiness_gate="Production",
        next_action=(
            "Define retention by identity, audit, "
            "chat, market, strategy, and model data."
        ),
    )
)


# ==========================================================
# OBSERVABILITY AND INCIDENT RESPONSE
# ==========================================================

observability_evidence = filenames_matching(
    [
        r"metric",
        r"trace",
        r"telemetry",
        r"observability",
        r"audit",
    ]
)

results.append(
    control(
        "OBS-001",
        "Observability",
        "Structured tracing, metrics, and audit evidence",
        pass_evidence=observability_evidence,
        required_gap=(
            "Observability coverage is incomplete."
        ),
        readiness_gate="Controlled Early User",
        next_action=(
            "Map every critical request, decision, "
            "AI call, and order lifecycle to "
            "correlated telemetry."
        ),
    )
)

alert_evidence = content_matching(
    [
        r"alertmanager",
        r"pagerduty",
        r"opsgenie",
        r"slack.*alert",
        r"alert rule",
        r"on-call",
        r"incident",
    ],
    path_patterns=[
        r"\.github/",
        r"backend/",
        r"scripts/",
        r".*\.md$",
    ],
)

results.append(
    control(
        "OBS-002",
        "Incident Operations",
        "Alerting and incident response",
        pass_evidence=alert_evidence,
        required_gap=(
            "Actionable alert routing, severity, "
            "ownership, and incident response are "
            "not fully proven."
        ),
        readiness_gate="Production",
        next_action=(
            "Define service-level alerts, escalation, "
            "incident roles, and post-incident review."
        ),
    )
)


# ==========================================================
# FINTECH CONTROLS
# ==========================================================

paper_live_evidence = content_matching(
    [
        r"paper.?trad",
        r"live.?trad",
        r"broker.*lock",
        r"execution.*lock",
        r"emergency.?stop",
        r"kill.?switch",
    ],
    path_patterns=[
        r"backend/app/stacks/",
    ],
)

results.append(
    control(
        "FIN-001",
        "FinTech Safety",
        "Paper/live execution separation",
        pass_evidence=paper_live_evidence,
        required_gap=(
            "A complete, runtime-qualified separation "
            "of paper and live execution is required."
        ),
        readiness_gate="Live Brokerage",
        next_action=(
            "Maintain live execution as NOT APPROVED "
            "until broker-side and end-to-end "
            "fail-closed qualification."
        ),
        blocked=True,
    )
)

risk_evidence = filenames_matching(
    [
        r"risk",
        r"kill_switch",
        r"drawdown",
        r"exposure",
        r"limit",
        r"loss_streak",
    ]
)

results.append(
    control(
        "FIN-002",
        "FinTech Risk",
        "Pre-trade and runtime risk controls",
        pass_evidence=risk_evidence,
        required_gap=(
            "Risk controls require end-to-end runtime "
            "qualification against every order path."
        ),
        readiness_gate="Live Brokerage",
        next_action=(
            "Prove risk checks cannot be bypassed by "
            "API, AI, admin, retry, or broker adapters."
        ),
        blocked=True,
    )
)

reconciliation_evidence = filenames_matching(
    [
        r"reconcil",
        r"accounting",
        r"ledger",
        r"audit",
        r"journal",
    ]
)

results.append(
    control(
        "FIN-003",
        "FinTech Operations",
        "Positions, cash, orders, and ledger reconciliation",
        pass_evidence=reconciliation_evidence,
        required_gap=(
            "Automated external broker-to-internal "
            "ledger reconciliation is not proven."
        ),
        readiness_gate="Live Brokerage",
        next_action=(
            "Qualify start-of-day, intraday, and "
            "end-of-day reconciliation with exception "
            "handling."
        ),
        blocked=True,
    )
)

approval_evidence = content_matching(
    [
        r"approval",
        r"four.?eyes",
        r"dual.?control",
        r"maker.?checker",
        r"human.?review",
        r"pending.?review",
    ],
    path_patterns=[
        r"backend/",
        r"handoff/",
        r".*\.md$",
    ],
)

results.append(
    control(
        "FIN-004",
        "FinTech Governance",
        "Human approval and segregation of duties",
        pass_evidence=approval_evidence,
        required_gap=(
            "Production-grade maker/checker and "
            "segregation-of-duties controls are not "
            "fully proven."
        ),
        readiness_gate="Live Brokerage",
        next_action=(
            "Define approval authority for strategy, "
            "risk, deployment, model, and live-order "
            "changes."
        ),
    )
)

audit_evidence = filenames_matching(
    [
        r"decision_event",
        r"audit",
        r"ledger",
        r"journal",
    ]
)

results.append(
    control(
        "FIN-005",
        "FinTech Auditability",
        "Immutable decision and execution evidence",
        pass_evidence=audit_evidence,
        required_gap=(
            "Tamper-evident retention and external "
            "verification of audit records is not "
            "fully proven."
        ),
        readiness_gate="Production",
        next_action=(
            "Add immutability controls, integrity "
            "verification, retention, and privileged "
            "access monitoring."
        ),
    )
)


# ==========================================================
# AI GOVERNANCE AND SAFETY
# ==========================================================

model_inventory = filenames_matching(
    [
        r"local_model_contract",
        r"model_registry",
        r"ollama",
        r"llm",
        r"model.*config",
    ]
)

results.append(
    control(
        "AI-001",
        "AI Governance",
        "Model inventory and approved-model contract",
        pass_evidence=model_inventory,
        required_gap=(
            "A complete approved-model inventory with "
            "version, purpose, owner, and risk class "
            "is not proven."
        ),
        readiness_gate="Controlled Early User",
        next_action=(
            "Freeze model identities, versions, "
            "capabilities, data access, and approved "
            "use cases."
        ),
    )
)

prompt_controls = filenames_matching(
    [
        r"prompt",
        r"role_overlay",
        r"context_assembler",
        r"truth",
        r"capability_state",
    ]
)

results.append(
    control(
        "AI-002",
        "AI Safety",
        "Prompt, context, and capability boundaries",
        pass_evidence=prompt_controls,
        required_gap=(
            "Prompt and capability controls require "
            "adversarial runtime qualification."
        ),
        readiness_gate="Controlled Early User",
        next_action=(
            "Run prompt-injection, role-confusion, "
            "tool-abuse, context-poisoning, and data "
            "exfiltration tests."
        ),
    )
)

grounding_evidence = content_matching(
    [
        r"grounded",
        r"tool_truth_state",
        r"evidence",
        r"truth boundary",
        r"citation",
    ],
    path_patterns=[
        r"backend/app/stacks/chat_public/",
        r"backend/app/stacks/wolfden_ai/",
    ],
)

results.append(
    control(
        "AI-003",
        "AI Reliability",
        "Grounding and evidence state",
        pass_evidence=grounding_evidence,
        required_gap=(
            "Grounding quality and unsupported-claim "
            "rates require measured evaluation."
        ),
        readiness_gate="Controlled Early User",
        next_action=(
            "Establish scored evaluations for factual "
            "accuracy, evidence use, refusal, and "
            "unsupported claims."
        ),
    )
)

evaluation_evidence = filenames_matching(
    [
        r"eval",
        r"benchmark",
        r"red.?team",
        r"adversarial",
        r"golden",
    ]
)

results.append(
    control(
        "AI-004",
        "AI Assurance",
        "Repeatable AI evaluation suite",
        pass_evidence=evaluation_evidence,
        required_gap=(
            "A versioned, release-gating AI evaluation "
            "suite was not fully proven."
        ),
        readiness_gate="Controlled Early User",
        next_action=(
            "Create golden tests, adversarial tests, "
            "regression thresholds, and release gates."
        ),
    )
)

ai_autonomy_evidence = content_matching(
    [
        r"human.?in.?the.?loop",
        r"approval",
        r"autonom",
        r"execution.?enabled",
        r"mutation.?enabled",
        r"tool.?permission",
    ],
    path_patterns=[
        r"backend/app/stacks/chat_public/",
        r"backend/app/stacks/wolfden_ai/",
        r"backend/app/stacks/execution/",
        r"backend/app/stacks/strategy/",
    ],
)

results.append(
    control(
        "AI-005",
        "AI Autonomy",
        "AI action authority and human oversight",
        pass_evidence=ai_autonomy_evidence,
        required_gap=(
            "Autonomous production actions remain "
            "unqualified."
        ),
        readiness_gate="AI Autonomy",
        next_action=(
            "Keep autonomous mutation, deployment, "
            "broker execution, and risk override "
            "NOT APPROVED."
        ),
        blocked=True,
    )
)


# ==========================================================
# TEST AND RELEASE QUALITY
# ==========================================================

test_count = count_test_files()

test_evidence = [
    f"Discovered project test files: {test_count}"
] if test_count else []

results.append(
    control(
        "QA-001",
        "Quality Engineering",
        "Automated test inventory",
        pass_evidence=test_evidence,
        required_gap=(
            "No meaningful automated test inventory "
            "was found."
        ),
        readiness_gate="Development",
        next_action=(
            "Measure coverage by critical runtime "
            "path rather than raw test count."
        ),
    )
)

coverage_evidence = existing_paths(
    [
        ".coveragerc",
        "coverage.xml",
    ]
) + content_matching(
    [
        r"pytest.*cov",
        r"coverage run",
        r"coverage report",
        r"coverageThreshold",
    ],
    path_patterns=[
        r"\.github/workflows/",
        r"pyproject",
        r"pytest",
        r"package\.json",
    ],
)

results.append(
    control(
        "QA-002",
        "Quality Engineering",
        "Coverage thresholds and release gating",
        pass_evidence=coverage_evidence,
        required_gap=(
            "Risk-based coverage thresholds and "
            "release gating were not proven."
        ),
        readiness_gate="Controlled Early User",
        next_action=(
            "Set coverage and mutation thresholds for "
            "auth, risk, execution, ledger, and AI "
            "boundaries."
        ),
    )
)

load_evidence = filenames_matching(
    [
        r"load",
        r"performance",
        r"benchmark",
        r"stress",
        r"phase136",
    ]
)

results.append(
    control(
        "QA-003",
        "Performance",
        "Load and capacity qualification evidence",
        pass_evidence=load_evidence,
        required_gap=(
            "Capacity testing must be repeated against "
            "the current integrated release."
        ),
        readiness_gate="Controlled Early User",
        next_action=(
            "Rerun load, soak, failure, and AI queue "
            "testing after Stage 5 hardening."
        ),
    )
)


# ==========================================================
# TOOLING STATE
# ==========================================================

tooling = {}

for name in (
    "git",
    "python3",
    "pytest",
    "node",
    "npm",
    "docker",
    "ollama",
):
    path = shutil.which(name)

    tooling[name] = {
        "available": path is not None,
        "path": path,
    }

git_status_code, git_status = run_command(
    [
        "git",
        "status",
        "--short",
    ]
)

git_branch_code, git_branch = run_command(
    [
        "git",
        "branch",
        "--show-current",
    ]
)

pytest_code, pytest_output = run_command(
    [
        "python3",
        "-m",
        "pytest",
        "-q",
        "backend/app/stacks/identity_auth/tests",
        "backend/app/stacks/chat_public/tests",
    ],
    timeout=120,
)


# ==========================================================
# READINESS SUMMARY
# ==========================================================

status_counts: dict[str, int] = {}

for item in results:
    status_counts[item.status] = (
        status_counts.get(
            item.status,
            0,
        )
        + 1
    )


def gate_status(
    gate: str,
) -> str:
    relevant = [
        item
        for item in results
        if item.readiness_gate == gate
    ]

    if not relevant:
        return "NOT ASSESSED"

    if any(
        item.status.startswith("BLOCKED")
        for item in relevant
    ):
        return "BLOCKED"

    if any(
        item.status == "MISSING"
        for item in relevant
    ):
        return "INCOMPLETE"

    if any(
        item.status == "PARTIAL"
        for item in relevant
    ):
        return "PARTIAL"

    return "QUALIFIED BY STATIC EVIDENCE"


readiness = {
    gate: gate_status(gate)
    for gate in (
        "Development",
        "Controlled Early User",
        "Production",
        "Live Brokerage",
        "AI Autonomy",
    )
}

payload = {
    "stage": "5A-B",
    "title": (
        "Normalized FinTech and AI DevOps "
        "Evidence Classification"
    ),
    "generated_at": datetime.now(
        UTC
    ).isoformat(),
    "repository": str(ROOT),
    "branch": (
        git_branch
        if git_branch_code == 0
        else None
    ),
    "scan_policy": {
        "read_only": True,
        "excluded_parts": sorted(
            EXCLUDED_PARTS
            | RUNTIME_EXCLUDED
        ),
        "source_file_count": len(
            SOURCE_FILES
        ),
        "test_file_count": test_count,
    },
    "tooling": tooling,
    "qualification": {
        "identity_and_chat_test_exit_code": (
            pytest_code
        ),
        "identity_and_chat_test_output": (
            pytest_output[-5000:]
        ),
    },
    "status_counts": status_counts,
    "readiness": readiness,
    "controls": [
        asdict(item)
        for item in results
    ],
    "git_status": {
        "exit_code": git_status_code,
        "output": git_status,
        "warning": (
            "Working-tree state is evidence only. "
            "Do not run git clean, git reset, or "
            "mass deletion."
        ),
    },
}

json_path = Path(
    os.environ["STAGE5A_JSON_REPORT"]
)

text_path = Path(
    os.environ["STAGE5A_TEXT_REPORT"]
)

json_path.write_text(
    json.dumps(
        payload,
        indent=2,
        sort_keys=False,
    )
    + "\n",
    encoding="utf-8",
)

lines: list[str] = []

lines.extend(
    [
        "=" * 88,
        "NEUROVEST",
        "STAGE 5A-B — NORMALIZED FINTECH / AI DEVOPS READINESS MATRIX",
        "=" * 88,
        f"Generated: {payload['generated_at']}",
        f"Repository: {ROOT}",
        f"Branch: {payload['branch']}",
        f"Source files inspected: {len(SOURCE_FILES)}",
        f"Test files discovered: {test_count}",
        "",
        "IMPORTANT:",
        (
            "This is a repository evidence assessment, "
            "not regulatory certification."
        ),
        (
            "No source files, database records, runtime "
            "services, or Git state were modified."
        ),
        (
            "Do not run git clean, git reset, or mass "
            "deletion based on this report."
        ),
        "",
        "=" * 88,
        "READINESS GATES",
        "=" * 88,
    ]
)

for gate, status in readiness.items():
    lines.append(
        f"{gate:28} {status}"
    )

lines.extend(
    [
        "",
        "=" * 88,
        "CONTROL SUMMARY",
        "=" * 88,
    ]
)

for status, count in sorted(
    status_counts.items()
):
    lines.append(
        f"{status:45} {count}"
    )

lines.extend(
    [
        "",
        "=" * 88,
        "CONTROL RESULTS",
        "=" * 88,
    ]
)

for item in results:
    lines.extend(
        [
            "",
            "-" * 88,
            (
                f"{item.control_id} | "
                f"{item.domain} | "
                f"{item.status}"
            ),
            "-" * 88,
            f"Control: {item.control}",
            (
                "Readiness gate: "
                f"{item.readiness_gate}"
            ),
            "Evidence:",
        ]
    )

    if item.evidence:
        for evidence in item.evidence[:20]:
            lines.append(
                f"  - {evidence}"
            )
    else:
        lines.append(
            "  - NONE LOCATED"
        )

    lines.append(
        "Gaps:"
    )

    if item.gaps:
        for gap in item.gaps:
            lines.append(
                f"  - {gap}"
            )
    else:
        lines.append(
            "  - No static evidence gap identified."
        )

    lines.append(
        f"Next action: {item.next_action}"
    )

lines.extend(
    [
        "",
        "=" * 88,
        "QUALIFICATION BASELINE",
        "=" * 88,
        (
            "Identity/chat test exit code: "
            f"{pytest_code}"
        ),
        "",
        pytest_output[-5000:],
        "",
        "=" * 88,
        "STAGE 5A-B DISPOSITION",
        "=" * 88,
    ]
)

if pytest_code == 0:
    lines.append(
        "PASS: Current identity-auth and chat-public "
        "test baseline remains green."
    )
else:
    lines.append(
        "BLOCKED: Current identity-auth/chat-public "
        "baseline contains failures."
    )

lines.extend(
    [
        "",
        (
            "Stage 5A-B is an evidence classification "
            "only."
        ),
        (
            "No Production, Live Brokerage, or AI "
            "Autonomy approval is granted by this scan."
        ),
        "=" * 88,
    ]
)

text_path.write_text(
    "\n".join(lines)
    + "\n",
    encoding="utf-8",
)

print(
    f"JSON report: {json_path}"
)

print(
    f"Text report: {text_path}"
)

print(
    f"Controls assessed: {len(results)}"
)

print(
    f"Source files inspected: {len(SOURCE_FILES)}"
)

print(
    f"Test files discovered: {test_count}"
)

print()

for gate, status in readiness.items():
    print(
        f"{gate}: {status}"
    )
