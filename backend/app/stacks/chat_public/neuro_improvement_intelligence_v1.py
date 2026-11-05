from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

VERSION = "neuro-improvement-intelligence-v1"

# A stack's existence means its source is present.
# It does NOT establish production readiness or qualification.
CAPABILITIES = {
    "identity_auth": {
        "label": "Authentication and identity",
        "priority": 100,
        "risk": "Unauthorized access",
    },
    "safety_governance": {
        "label": "Safety governance and trading controls",
        "priority": 100,
        "risk": "Unauthorized or unsafe execution",
    },
    "chat_public": {
        "label": "User and developer chat",
        "priority": 95,
        "risk": "Unreliable or ungrounded responses",
    },
    "db_runtime": {
        "label": "Database runtime and persistence",
        "priority": 95,
        "risk": "Incorrect or lost persistent state",
    },
    "risk": {
        "label": "Portfolio and strategy risk controls",
        "priority": 95,
        "risk": "Incorrect financial risk assessment",
    },
    "market_data": {
        "label": "Market data",
        "priority": 85,
        "risk": "Stale or invalid market information",
    },
    "strategy": {
        "label": "Strategy management and validation",
        "priority": 85,
        "risk": "Incorrect strategy qualification",
    },
    "portfolio": {
        "label": "Portfolio analysis",
        "priority": 85,
        "risk": "Incorrect portfolio state",
    },
    "research": {
        "label": "Research and retrieval",
        "priority": 80,
        "risk": "Unsupported research conclusions",
    },
    "paper_trading": {
        "label": "Simulation and paper trading",
        "priority": 80,
        "risk": "Incorrect simulated execution",
    },
    "broker_integration": {
        "label": "Broker integration",
        "priority": 100,
        "risk": "Unapproved live financial execution",
    },
    "ai_chat": {
        "label": "AI reasoning infrastructure",
        "priority": 85,
        "risk": "Unavailable or incorrectly routed models",
    },
    "execution": {
        "label": "Execution infrastructure",
        "priority": 100,
        "risk": "Uncontrolled order execution",
    },
    "journal_ledger": {
        "label": "Journal and ledger",
        "priority": 85,
        "risk": "Incomplete audit history",
    },
    "wolfden_ai": {
        "label": "AI training and development workflows",
        "priority": 80,
        "risk": "Unqualified autonomous changes",
    },
    "notification": {
        "label": "Notification delivery",
        "priority": 65,
        "risk": "Missing important user notifications",
    },
    "admin_control": {
        "label": "Administrative controls",
        "priority": 95,
        "risk": "Incorrect privileged operations",
    },
    "runtime": {
        "label": "Runtime operations",
        "priority": 95,
        "risk": "Runtime instability",
    },
}

# These fields are specifically limited to non-sensitive
# operational signals already produced by qualification runs.
SAFE_EVIDENCE_FIELDS = (
    "decision",
    "source_integrity",
    "comparison_complete",
    "no_new_regressions",
    "expanded_regressions_passed",
    "regressions_passed",
    "complete_http_matrix",
    "generated_persisted_returned_hashes_equal",
    "release_integrity",
    "production_case_count",
    "candidate_case_count",
    "new_regressions",
    "shared_failures",
    "incomplete_batches",
    "unresolved_processes",
)

def _safe_evidence(path):
    try:
        if path.stat().st_size > 256_000:
            return None

        raw = json.loads(path.read_text(encoding="utf-8"))

        if not isinstance(raw, dict):
            return None

        clean = {}

        for field in SAFE_EVIDENCE_FIELDS:
            value = raw.get(field)

            if isinstance(value, bool) or value is None:
                clean[field] = value
            elif isinstance(value, (int, float)):
                clean[field] = value
            elif isinstance(value, str):
                if field == "decision":
                    clean[field] = value[:120]
            elif isinstance(value, list):
                # Never export the list contents:
                # test names or records could expose details.
                clean[field + "_count"] = len(value)

        if not isinstance(clean.get("decision"), str):
            return None

        return clean

    except (OSError, ValueError, UnicodeError):
        return None

def evidence_inventory(root, max_runs=100):
    """
    Discover qualification evidence across the repository.

    Important qualification reports are located explicitly by
    run family, rather than being lost inside an arbitrary
    alphabetical first-100 directory window.

    Reads allowlisted scalar evidence only.
    Never reads conversation content or raw secrets.
    """
    qualification = Path(root) / "runtime/qualification"

    if not qualification.is_dir():
        return []

    important_prefixes = (
        "neuro_developer_evidence_R52_",
        "neuro_developer_evidence_R55_",
        "neuro_developer_evidence_R56_",
        "neuro_developer_evidence_R63_",
    )

    directories = [
        path
        for path in qualification.iterdir()
        if path.is_dir() and not path.is_symlink()
    ]

    def ordering(path):
        # Run names end in UTC timestamps. For recognized
        # run families this preserves newest-first ordering.
        import re
        match = re.search(
            r"(20[0-9]{6}T[0-9]{6}Z)$",
            path.name,
        )
        return (
            match.group(1) if match else "",
            path.name,
        )

    directories.sort(key=ordering, reverse=True)

    important = [
        path for path in directories
        if path.name.startswith(important_prefixes)
    ]

    # Always include every important qualification run.
    # Additionally inspect the most recent general evidence
    # directories for ongoing progress.
    selected = list(important)
    seen = {path.name for path in selected}

    for path in directories:
        if len(selected) >= len(important) + max_runs:
            break
        if path.name not in seen:
            selected.append(path)
            seen.add(path.name)

    records = []

    for directory in selected:
        for filename in (
            "qualification.json",
            "manifest.json",
            "report.json",
        ):
            evidence_file = directory / filename

            if (
                not evidence_file.is_file()
                or evidence_file.is_symlink()
            ):
                continue

            evidence = _safe_evidence(evidence_file)

            if evidence is None:
                continue

            records.append({
                "run": directory.name,
                "evidence": evidence,
            })
            break

    records.sort(
        key=lambda item: ordering(
            Path(item["run"])
        ),
        reverse=True,
    )

    return records


def capability_inventory(root):
    """
    Inspect actual backend Python architecture.

    Presence is not qualification.
    An absent expected path is not proof of missing functionality.
    """
    root = Path(root).resolve()
    app = root / "backend/app"
    stack_root = app / "stacks"

    result = []

    # Only inspect source paths; never import modules, run
    # code, inspect secrets, or read application databases.
    all_directories = []

    if app.is_dir():
        for path in app.rglob("*"):
            if (
                path.is_dir()
                and not path.is_symlink()
                and len(path.relative_to(app).parts) <= 5
                and not any(part in (
                    "__pycache__", ".git", ".venv",
                    "node_modules", "runtime", "qualification",
                ) for part in path.relative_to(app).parts[:-1])
            ):
                all_directories.append(path)

    aliases = {
        "identity_auth": ("identity_auth", "authentication", "identity"),
        "safety_governance": ("safety_governance", "governance", "safety"),
        "chat_public": ("chat_public",),
        "db_runtime": ("db_runtime", "database", "db_model"),
        "risk": ("risk", "risk_management"),
        "market_data": ("market_data",),
        "strategy": ("strategy", "strategies"),
        "portfolio": ("portfolio",),
        "research": ("research",),
        "paper_trading": ("paper_trading", "simulation"),
        "broker_integration": ("broker_integration", "broker", "snaptrade"),
        "ai_chat": ("ai_chat",),
        "execution": ("execution",),
        "journal_ledger": ("journal_ledger", "ledger", "journal"),
        "wolfden_ai": ("wolfden_ai", "wolfden", "training"),
        "notification": ("notification", "notifications"),
        "admin_control": ("admin_control", "admin"),
        "runtime": ("runtime", "runtime_control", "operations"),
    }

    for key, definition in CAPABILITIES.items():
        expected = stack_root / key
        exact = expected.is_dir() and not expected.is_symlink()
        names = aliases.get(key, (key,))

        matches = sorted({
            str(path.relative_to(root))
            for path in all_directories
            if path.name.casefold() in names
        })

        if exact:
            state = "source_directory_present"
        elif matches:
            state = "possible_alternate_location"
        else:
            state = "location_unverified"

        result.append({
            "id": key,
            "name": definition["label"],
            "source_present": exact or bool(matches),
            "source_discovery_state": state,
            "expected_path": str(expected.relative_to(root)),
            "possible_source_locations": matches[:8],
            "qualification": "not_established",
            "production_ready": False,
            "priority": definition["priority"],
            "risk": definition["risk"],
        })

    return result


def _latest_matching(records, prefix):
    for record in records:
        decision = record["evidence"].get("decision", "")

        if decision.startswith(prefix):
            return record

    return None

def _hash_record(record):
    payload = json.dumps(
        record,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:16]

def build_assessment(root):
    root = Path(root).resolve()

    inventory = capability_inventory(root)
    evidence = evidence_inventory(root)

    checks = {
        "developer_http_security": {
            "prefix": "R52_",
            "expected": (
                "R52_FULL_ISOLATED_HTTP_AUTHORIZATION_MATRIX_QUALIFIED"
            ),
        },
        "candidate_compatibility": {
            "prefix": "R55_",
            "expected": (
                "R55_STAGED_CANDIDATE_COMPATIBILITY_QUALIFIED"
            ),
        },
        "expanded_chat_regressions": {
            "prefix": "R56_",
            "expected": (
                "R56_EXPANDED_STAGED_CHAT_REGRESSIONS_QUALIFIED"
            ),
        },
        "differential_regressions": {
            "prefix": "R63_",
            "expected": (
                "R63_NO_NEW_REGRESSIONS_BASELINE_DEBT"
            ),
        },
    }

    qualifications = {}

    for name, contract in checks.items():
        found = _latest_matching(
            evidence,
            contract["prefix"],
        )

        actual = (
            found["evidence"]["decision"]
            if found else None
        )

        qualifications[name] = {
            "status": (
                "qualified"
                if actual == contract["expected"]
                else "pending" if actual
                else "no_evidence"
            ),
            "decision": actual,
            "evidence_run": (
                found["run"] if found else None
            ),
        }

    findings = []

    def add(fid, title, impact, effort, urgency,
            capability, observation, next_action,
            validation, confidence="medium"):
        item = {
            "id": fid,
            "title": title,
            "capability": capability,
            "impact": impact,
            "effort": effort,
            "urgency": urgency,
            "confidence": confidence,
            "observation": observation,
            "next_action": next_action,
            "validation": validation,
            "developer_authorization_required": True,
        }
        item["score"] = round(
            impact * 0.5
            + urgency * 0.4
            - effort * 0.1,
            2,
        )
        findings.append(item)

    # Architecture discrepancies remain discovery tasks,
    # not claims that entire features are missing.
    uncertain = [
        item for item in inventory
        if item["source_discovery_state"] == "location_unverified"
    ]

    if uncertain:
        add(
            "architecture_capability_mapping",
            "Map unverified capability implementation locations",
            65, 35, 60, "chat_public",
            str(len(uncertain))
            + " tracked capabilities have no verified source directory "
            "at an expected or recognized alternate location.",
            "Inspect their real implementation contracts, route wiring, "
            "and tests; do not create duplicate stacks based on names.",
            "Require reviewed source paths and behavior evidence "
            "before marking an implementation present or absent.",
        )

    if qualifications["expanded_chat_regressions"]["status"] != "qualified":
        add(
            "chat_regression_debt",
            "Resolve remaining chat regression failures",
            90, 45, 90, "chat_public",
            "Expanded chat regression qualification is not complete.",
            "Classify baseline failures, correct outdated contracts, "
            "and isolate external model-dependent tests.",
            "Run the corrected tests against the staged candidate.",
        )

    if qualifications["differential_regressions"]["status"] != "qualified":
        add(
            "candidate_differential_gap",
            "Complete production-versus-candidate compatibility",
            90, 55, 85, "runtime",
            "Full differential regression evidence is incomplete.",
            "Stabilize the test environment and compare equivalent "
            "test cases without masking failures.",
            "Require complete matching case coverage.",
        )

    if qualifications["developer_http_security"]["status"] != "qualified":
        add(
            "developer_evidence_authorization",
            "Qualify developer-only evidence access",
            100, 60, 100, "identity_auth",
            "Developer HTTP security qualification not established.",
            "Validate JWT identity, ordinary-user isolation, "
            "forged-role rejection and thread ownership.",
            "Execute authenticated HTTP negative and positive tests.",
        )

    if qualifications["candidate_compatibility"]["status"] != "qualified":
        add(
            "staged_runtime_binding",
            "Verify staged chat runtime binding",
            95, 45, 90, "chat_public",
            "Staged candidate compatibility not established.",
            "Bind API imports to candidate modules and execute regressions.",
            "Verify imported module paths and HTTP handler binding.",
        )

    # No real database or production deployment qualification
    # is inferred from isolated tests.
    add(
        "persistent_progress_tracking",
        "Persist qualification-linked improvement progress",
        85, 60, 75, "journal_ledger",
        "Improvement lifecycle persistence has not been qualified.",
        "Build owner-scoped persistence and evidence-hash transitions.",
        "Test authorization, idempotency and transition integrity.",
    )

    add(
        "controlled_beta_integration",
        "Validate controlled beta integration",
        95, 70, 85, "runtime",
        "Isolated candidate qualification does not establish "
        "beta deployment readiness.",
        "Qualify integration, rollback, operational monitoring "
        "and developer authorization.",
        "Require deployment-specific approval and rollback validation.",
    )

    findings.sort(
        key=lambda item: (-item["score"], item["id"])
    )

    return {
        "schema_version": VERSION,
        "inventory": inventory,
        "qualifications": qualifications,
        "recommendations": findings,
        "evidence_runs_scanned": len(evidence),
        "safety": {
            "live_trading_approved": False,
            "automatic_deployment_approved": False,
            "developer_approval_required": True,
            "assessment_is_read_only": True,
        },
    }

def update_progress(previous, current):
    previous_map = {
        x["id"]: x
        for x in previous.get("recommendations", [])
    }

    prior_quals = previous.get("qualifications", {})
    current_quals = current.get("qualifications", {})

    transitions = []

    for name, now in current_quals.items():
        was = prior_quals.get(name, {})
        old_status = was.get("status", "not_observed")
        new_status = now.get("status", "no_evidence")

        if old_status != new_status:
            transitions.append({
                "kind": "qualification",
                "id": name,
                "from": old_status,
                "to": new_status,
                "evidence_run": now.get("evidence_run"),
            })

    current_ids = {
        x["id"]
        for x in current.get("recommendations", [])
    }

    resolved_candidates = sorted(
        set(previous_map) - current_ids
    )

    # A removed recommendation is not automatically considered
    # resolved: developers must verify supporting evidence.
    for fid in resolved_candidates:
        transitions.append({
            "kind": "recommendation",
            "id": fid,
            "from": "open",
            "to": "requires_resolution_review",
        })

    return transitions

def render_developer_report(report, limit=6):
    lines = [
        "NEURO IMPROVEMENT INTELLIGENCE",
        "",
        "Capability inventory: "
        + str(len(report["inventory"]))
        + " tracked systems.",
        "Evidence runs evaluated: "
        + str(report["evidence_runs_scanned"]),
        "",
        "Qualification status:",
    ]

    for key, value in report["qualifications"].items():
        lines.append(
            "- " + key + ": " + value["status"]
            + " (" + str(value["decision"] or "no report") + ")"
        )

    lines.extend(["", "Priority improvements:"])

    for index, item in enumerate(
        report["recommendations"][:limit],
        1,
    ):
        lines.extend([
            str(index) + ". " + item["title"],
            "   Evidence: " + item["observation"],
            "   Action: " + item["next_action"],
            "   Validation: " + item["validation"],
        ])

    lines.extend([
        "",
        "Evidence limits: source presence is not production "
        "qualification. Unverified integrations remain pending.",
        "Developer approval required for modifications and deployment.",
        "Live broker orders remain unauthorized.",
    ])

    return "\n".join(lines)

def assess_developer_improvements(root):
    report = build_assessment(root)
    report["evidence_fingerprint"] = _hash_record({
        "qualifications": report["qualifications"],
        "recommendations": report["recommendations"],
    })
    return {
        "status": "ok",
        "answer": render_developer_report(report),
        "report": report,
    }



def write_progress_snapshot(report, destination, previous=None):
    """
    Write a local review snapshot with evidence fingerprint
    and explicit transitions. No automatic approval or resolution.
    """
    import os

    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

    if destination.is_symlink():
        raise ValueError("Refusing symlink snapshot target")

    transitions = (
        update_progress(previous, report)
        if previous is not None else []
    )

    content = {
        "schema_version": "neuro-improvement-progress-v1",
        "evidence_fingerprint": _hash_record({
            "qualifications": report["qualifications"],
            "recommendations": report["recommendations"],
        }),
        "qualification_states": {
            name: row["status"]
            for name, row in report["qualifications"].items()
        },
        "open_recommendation_ids": [
            row["id"] for row in report["recommendations"]
        ],
        "transitions": transitions,
        "review_required": True,
        "developer_authorization_required": True,
        "deployment_approved": False,
        "live_trading_approved": False,
    }

    temporary = destination.with_name(destination.name + ".tmp")
    with temporary.open("x", encoding="utf-8") as stream:
        os.chmod(temporary, 0o600)
        json.dump(content, stream, indent=2)
        stream.write("\n")

    temporary.replace(destination)
    return content



def assess_developer_backlog(root, previous_backlog=None):
    """
    Read-only planning interface used after developer
    authorization by the surrounding application.
    """
    backlog_engine = _load_local_intelligence_component(
        "neuro_improvement_backlog_v1.py",
        "neuro_f6_backlog_engine",
    )

    assessment = assess_developer_improvements(root)
    backlog = backlog_engine.reconcile(
        assessment["report"], previous_backlog
    )

    return {
        "status": "ok",
        "answer": (
            assessment["answer"]
            + "\n\n"
            + backlog_engine.render(backlog)
        ),
        "report": assessment["report"],
        "backlog": backlog,
    }



# F5: add source-backed feature intelligence while retaining
# the existing F4 qualification and improvement assessment.

_neuro_f4_assess_developer_improvements = (
    assess_developer_improvements
)

def assess_developer_improvements(root):
    from pathlib import Path
    feature_engine = _load_local_intelligence_component(
        "neuro_feature_intelligence_v1.py",
        "neuro_f6_feature_engine",
    )

    original = _neuro_f4_assess_developer_improvements(root)

    payload = dict(original["report"])
    payload["_root"] = str(Path(root).resolve())

    expanded = feature_engine.extend_assessment(payload)

    contracts = feature_engine.discover_route_contracts(root)

    expanded["route_contract_summary"] = {
        "contract_count": contracts["contract_count"],
        "truncated": contracts["truncated"],
        "mounted": "unverified",
        "authorization": "unverified",
        "test_coverage": "unverified",
    }

    return {
        "status": original["status"],
        "answer": (
            original["answer"]
            + "\n\n"
            + feature_engine.render_feature_summary(
                expanded["feature_inventory"]
            )
        ),
        "report": expanded,
    }



def _load_local_intelligence_component(filename, module_name):
    """
    Load an explicitly named candidate sibling.

    No app-root sys.path changes and no arbitrary caller paths.
    """
    import importlib.util
    from pathlib import Path

    allowed = {
        "neuro_feature_intelligence_v1.py",
        "neuro_improvement_backlog_v1.py",
    }

    if filename not in allowed:
        raise ValueError("Unapproved intelligence component")

    path = Path(__file__).resolve().parent / filename

    if not path.is_file() or path.is_symlink():
        raise FileNotFoundError("Candidate component missing")

    spec = importlib.util.spec_from_file_location(
        module_name, path
    )

    if spec is None or spec.loader is None:
        raise ImportError("Cannot load candidate component")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module
