#!/usr/bin/env python3
"""
NeuroVest Integrated Qualification Campaign

IQC Remediation Batch 2 —
auth_identity Implementation-State Classification,
Placeholder Boundary Qualification, and Security Roadmap Freeze

This batch does not implement:
- user profiles
- JWT issuance or verification
- token expiry or refresh
- sessions
- SnapTrade connectivity
- Cerberus security controls

It determines:
1. What auth_identity currently contains.
2. Whether placeholders are dormant and fail-closed.
3. Whether production routes falsely assume authentication exists.
4. What remains before Auth and SnapTrade can safely be added.
5. What remains for Cerberus:
   - External Threat Head
   - Internal Threat Head
   - Streaming Threat Head
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(".").resolve()

BACKEND_ROOT = ROOT / "backend" / "app"
STACKS_ROOT = BACKEND_ROOT / "stacks"

AUTH_ROOT = STACKS_ROOT / "auth_identity"
SNAPTRADE_ROOT = STACKS_ROOT / "snaptrade"

RUNTIME_ROOT = ROOT / "runtime"

OUTPUT_DIR = (
    RUNTIME_ROOT
    / "iqc"
    / "remediation_batch2"
)

STAGE1B_REPORT = (
    RUNTIME_ROOT
    / "iqc"
    / "stage1b"
    / "iqc_stage1b_calibrated_baseline_latest.json"
)

STAGE2_REPORT = (
    RUNTIME_ROOT
    / "iqc"
    / "stage2"
    / "iqc_stage2_targeted_remediation_plan_latest.json"
)

BATCH1_REPORT = (
    RUNTIME_ROOT
    / "iqc"
    / "remediation_batch1"
    / "iqc_remediation_batch1_latest.json"
)

IMPORT_AUDIT = (
    RUNTIME_ROOT
    / "hardening"
    / "workstream1"
    / "import_cycle_audit_latest.json"
)

REPORT_JSON = (
    OUTPUT_DIR
    / "iqc_remediation_batch2_auth_roadmap_latest.json"
)

REPORT_TEXT = (
    OUTPUT_DIR
    / "iqc_remediation_batch2_auth_roadmap_latest.txt"
)

EVIDENCE_JSON = (
    OUTPUT_DIR
    / "iqc_remediation_batch2_auth_evidence_latest.json"
)

FREEZE_JSON = (
    OUTPUT_DIR
    / "iqc_remediation_batch2_roadmap_freeze_latest.json"
)

PLACEHOLDER_MARKERS = (
    "todo",
    "not implemented",
    "notimplementederror",
    "placeholder",
    "stub",
    "coming soon",
)

AUTH_IMPLEMENTATION_MARKERS = {
    "user_profile_model": (
        "userprofile",
        "user_profile",
        "profilemodel",
    ),
    "user_repository": (
        "userrepository",
        "user_repository",
    ),
    "password_hashing": (
        "password_hash",
        "verify_password",
        "bcrypt",
        "argon2",
        "passlib",
    ),
    "jwt_issue": (
        "create_access_token",
        "issue_token",
        "jwt.encode",
    ),
    "jwt_verify": (
        "verify_token",
        "decode_token",
        "jwt.decode",
    ),
    "access_token_expiry": (
        "access_token_expire",
        "expires_delta",
        "exp",
    ),
    "refresh_tokens": (
        "refresh_token",
        "rotate_refresh",
    ),
    "token_revocation": (
        "revoke_token",
        "token_blacklist",
        "revoked_token",
    ),
    "session_persistence": (
        "session_repository",
        "user_session",
        "session_store",
    ),
    "auth_rate_limits": (
        "rate_limit",
        "login_attempt",
        "throttle",
    ),
    "token_fetch_timeout": (
        "token_timeout",
        "request_timeout",
        "connect_timeout",
    ),
}

FAIL_OPEN_PATTERNS = {
    "anonymous_allowed_default": re.compile(
        r"\ballow_anonymous\s*[:=]\s*True\b",
        re.IGNORECASE,
    ),
    "auth_disabled": re.compile(
        r"\bauth(?:entication)?_enabled\s*[:=]\s*False\b",
        re.IGNORECASE,
    ),
    "always_authenticated": re.compile(
        r"\bis_authenticated\s*[:=]\s*True\b",
        re.IGNORECASE,
    ),
    "verification_bypass": re.compile(
        r"\bskip_(?:auth|authentication|verification)\s*[:=]\s*True\b",
        re.IGNORECASE,
    ),
}

ROUTE_DECORATOR_PATTERN = re.compile(
    r"@\w+\.(get|post|put|patch|delete|route)\s*\(",
    re.IGNORECASE,
)

AUTH_ENFORCEMENT_MARKERS = (
    "depends(",
    "require_user",
    "require_auth",
    "current_user",
    "authenticated_user",
    "verify_token",
    "security(",
    "oauth2",
    "authorization",
)

SENSITIVE_ROUTE_MARKERS = (
    "portfolio",
    "account",
    "broker",
    "snaptrade",
    "trade",
    "order",
    "execution",
    "admin",
    "user",
    "profile",
    "token",
    "connect",
)

SNAPTRADE_MARKERS = {
    "package_exists": (),
    "client_adapter": (
        "client",
        "adapter",
        "snaptrade",
    ),
    "connection_flow": (
        "register_user",
        "connection_portal",
        "connect_broker",
    ),
    "user_mapping": (
        "user_id",
        "snaptrade_user",
    ),
    "secret_management": (
        "client_secret",
        "secret_key",
        "environment",
    ),
    "token_storage": (
        "access_token",
        "authorization_id",
        "token_repository",
    ),
    "timeout_retry": (
        "timeout",
        "retry",
        "backoff",
    ),
    "webhook_verification": (
        "webhook",
        "signature",
    ),
    "paper_only_guard": (
        "paper_only",
        "paper trading",
        "live trading disabled",
    ),
    "risk_gate": (
        "risk",
        "kill_switch",
    ),
    "audit_logging": (
        "audit",
        "journal",
        "ledger",
    ),
}

CERBERUS_TRACKS = {
    "external_threat_head": {
        "description": (
            "Watches internet-facing threats, hostile requests, "
            "credential attacks, dependency exposure, and edge abuse."
        ),
        "milestones": {
            "authenticated_edge_boundary": (
                "require_auth",
                "authentication",
                "oauth2",
                "jwt",
            ),
            "rate_limiting": (
                "rate_limit",
                "throttle",
            ),
            "request_validation": (
                "validation",
                "schema",
                "validator",
            ),
            "secret_management": (
                "secret",
                "vault",
                "keyring",
            ),
            "dependency_security": (
                "dependency",
                "vulnerability",
                "security audit",
            ),
            "external_attack_logging": (
                "security_event",
                "attack_log",
                "threat_log",
            ),
        },
    },
    "internal_threat_head": {
        "description": (
            "Watches unauthorized internal actions, privilege misuse, "
            "service boundary violations, and integrity changes."
        ),
        "milestones": {
            "role_based_access": (
                "rbac",
                "role",
                "permission",
            ),
            "service_authorization": (
                "service_auth",
                "capability",
                "authorization",
            ),
            "least_privilege": (
                "least_privilege",
                "deny_by_default",
            ),
            "integrity_monitoring": (
                "integrity",
                "hash",
                "manifest",
            ),
            "privileged_action_audit": (
                "admin_audit",
                "privileged_event",
                "decision_audit",
            ),
            "internal_anomaly_detection": (
                "internal_threat",
                "anomaly",
                "behavior_monitor",
            ),
        },
    },
    "streaming_threat_head": {
        "description": (
            "Watches live streams, WebSockets, event channels, replay, "
            "session hopping, packet-flow anomalies, and stream abuse."
        ),
        "milestones": {
            "stream_authentication": (
                "websocket_auth",
                "stream_auth",
            ),
            "replay_protection": (
                "nonce",
                "replay",
                "sequence_number",
            ),
            "session_hopping_detection": (
                "session_hop",
                "session_binding",
                "device_binding",
            ),
            "stream_rate_limits": (
                "stream_rate",
                "message_rate",
            ),
            "packet_flow_anomaly_detection": (
                "packet",
                "flow_anomaly",
                "network_anomaly",
            ),
            "stream_telemetry": (
                "stream_metrics",
                "stream_telemetry",
                "connection_metrics",
            ),
        },
    },
}


def load_json(
    path: Path,
) -> dict[str, Any]:
    assert path.is_file(), (
        f"Required evidence missing: {path}"
    )

    value = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert isinstance(
        value,
        dict,
    )

    return value


def relative(
    path: Path,
) -> str:
    return path.relative_to(
        ROOT
    ).as_posix()


def sha256_file(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def python_files(
    root: Path,
) -> list[Path]:
    if not root.is_dir():
        return []

    return [
        path
        for path in sorted(
            root.rglob("*.py")
        )
        if "__pycache__" not in path.parts
    ]


def repository_text() -> str:
    parts = []

    for path in python_files(
        BACKEND_ROOT
    ):
        parts.append(
            path.read_text(
                encoding="utf-8",
                errors="replace",
            ).lower()
        )

    return "\n".join(parts)


def inspect_python(
    path: Path,
) -> dict[str, Any]:
    source = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    lowered = source.lower()

    try:
        tree = ast.parse(
            source,
            filename=str(path),
        )

    except SyntaxError as exc:
        return {
            "path": relative(path),
            "sha256": sha256_file(path),
            "syntax_valid": False,
            "syntax_error": str(exc),
            "classes": [],
            "functions": [],
            "async_functions": [],
            "imports": [],
            "placeholder_markers": [],
            "fail_open_signals": [],
        }

    classes = sorted(
        {
            node.name
            for node in ast.walk(tree)
            if isinstance(
                node,
                ast.ClassDef,
            )
        }
    )

    functions = sorted(
        {
            node.name
            for node in ast.walk(tree)
            if isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            )
        }
    )

    async_functions = sorted(
        {
            node.name
            for node in ast.walk(tree)
            if isinstance(
                node,
                ast.AsyncFunctionDef,
            )
        }
    )

    imports = set()

    for node in ast.walk(tree):
        if isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                imports.add(
                    alias.name
                )

        elif isinstance(
            node,
            ast.ImportFrom,
        ) and node.module:
            imports.add(
                node.module
            )

    placeholders = [
        marker
        for marker in PLACEHOLDER_MARKERS
        if marker in lowered
    ]

    fail_open = [
        name
        for name, pattern
        in FAIL_OPEN_PATTERNS.items()
        if pattern.search(source)
    ]

    return {
        "path": relative(path),
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
        "syntax_valid": True,
        "classes": classes,
        "functions": functions,
        "async_functions": async_functions,
        "imports": sorted(imports),
        "placeholder_markers": placeholders,
        "fail_open_signals": fail_open,
    }


def detect_markers(
    text: str,
    marker_map: dict[
        str,
        tuple[str, ...],
    ],
) -> dict[str, Any]:
    results = {}

    for name, markers in marker_map.items():
        if name == "package_exists":
            detected = SNAPTRADE_ROOT.is_dir()
            evidence = (
                [relative(SNAPTRADE_ROOT)]
                if detected
                else []
            )

        else:
            matched = [
                marker
                for marker in markers
                if marker.lower() in text
            ]

            detected = bool(matched)
            evidence = matched

        results[name] = {
            "detected": detected,
            "evidence": evidence,
        }

    return results


def implementation_percentage(
    milestones: dict[str, Any],
) -> float:
    if not milestones:
        return 0.0

    completed = sum(
        1
        for value in milestones.values()
        if value.get(
            "detected"
        )
    )

    return round(
        100.0
        * completed
        / len(milestones),
        1,
    )


def auth_external_consumers() -> list[
    dict[str, Any]
]:
    consumers = []

    for path in python_files(
        BACKEND_ROOT
    ):
        if AUTH_ROOT in path.parents:
            continue

        source = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        lowered = source.lower()

        tokens = (
            "stacks.auth_identity",
            "stacks/auth_identity",
            "auth_identity.",
        )

        if not any(
            token in lowered
            for token in tokens
        ):
            continue

        consumers.append(
            {
                "path": relative(path),
                "is_test": (
                    "test" in path.parts
                    or "tests" in path.parts
                    or path.name.startswith(
                        "test_"
                    )
                ),
            }
        )

    return consumers


def route_inventory() -> list[
    dict[str, Any]
]:
    routes = []

    for path in python_files(
        BACKEND_ROOT
    ):
        source = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        if not ROUTE_DECORATOR_PATTERN.search(
            source
        ):
            continue

        lowered = source.lower()

        auth_enforced = any(
            marker in lowered
            for marker in AUTH_ENFORCEMENT_MARKERS
        )

        sensitive_markers = [
            marker
            for marker in SENSITIVE_ROUTE_MARKERS
            if marker in lowered
        ]

        routes.append(
            {
                "path": relative(path),
                "auth_enforcement_detected": (
                    auth_enforced
                ),
                "sensitive_markers": (
                    sensitive_markers
                ),
                "potential_sensitive_unauthenticated": (
                    bool(
                        sensitive_markers
                    )
                    and not auth_enforced
                ),
            }
        )

    return routes


def cerberus_inventory(
    repo_text: str,
) -> dict[str, Any]:
    result = {}

    for track, definition in (
        CERBERUS_TRACKS.items()
    ):
        milestones = {}

        for milestone, markers in (
            definition[
                "milestones"
            ].items()
        ):
            matched = [
                marker
                for marker in markers
                if marker.lower()
                in repo_text
            ]

            milestones[
                milestone
            ] = {
                "detected": bool(
                    matched
                ),
                "evidence": matched,
            }

        result[
            track
        ] = {
            "description": definition[
                "description"
            ],
            "milestones": milestones,
            "provisional_completeness": (
                implementation_percentage(
                    milestones
                )
            ),
        }

    return result


def source_manifest() -> dict[str, Any]:
    entries = []

    for path in python_files(
        BACKEND_ROOT
    ):
        entries.append(
            {
                "path": relative(path),
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
        )

    digest = hashlib.sha256()

    for entry in entries:
        digest.update(
            entry[
                "path"
            ].encode(
                "utf-8"
            )
        )

        digest.update(
            entry[
                "sha256"
            ].encode(
                "ascii"
            )
        )

    return {
        "file_count": len(entries),
        "manifest_sha256": (
            digest.hexdigest()
        ),
        "files": entries,
    }


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    assert AUTH_ROOT.is_dir(), (
        "auth_identity stack does not exist"
    )

    stage1b = load_json(
        STAGE1B_REPORT
    )

    stage2 = load_json(
        STAGE2_REPORT
    )

    batch1 = load_json(
        BATCH1_REPORT
    )

    import_audit = load_json(
        IMPORT_AUDIT
    )

    assert stage1b[
        "status"
    ] == "completed"

    assert stage2[
        "status"
    ] == "completed"

    assert batch1[
        "status"
    ] == "completed"

    assert batch1[
        "whole_backend_tests"
    ][
        "passed"
    ] >= 143

    assert batch1[
        "whole_backend_tests"
    ][
        "failed"
    ] == 0

    assert batch1[
        "source_integrity"
    ][
        "production_source_modified"
    ] is False

    summary = import_audit[
        "summary"
    ]

    assert summary[
        "active_internal_unresolved"
    ] == 0

    assert summary[
        "active_cycle_components"
    ] == 0

    auth_files = python_files(
        AUTH_ROOT
    )

    auth_records = [
        inspect_python(path)
        for path in auth_files
    ]

    auth_text = "\n".join(
        path.read_text(
            encoding="utf-8",
            errors="replace",
        ).lower()
        for path in auth_files
    )

    auth_milestones = detect_markers(
        auth_text,
        AUTH_IMPLEMENTATION_MARKERS,
    )

    consumers = (
        auth_external_consumers()
    )

    production_consumers = [
        item
        for item in consumers
        if not item[
            "is_test"
        ]
    ]

    routes = route_inventory()

    sensitive_unauthenticated = [
        route
        for route in routes
        if route[
            "potential_sensitive_unauthenticated"
        ]
    ]

    fail_open_signals = [
        {
            "path": record[
                "path"
            ],
            "signals": record[
                "fail_open_signals"
            ],
        }
        for record in auth_records
        if record[
            "fail_open_signals"
        ]
    ]

    syntax_errors = [
        record
        for record in auth_records
        if not record[
            "syntax_valid"
        ]
    ]

    placeholder_files = [
        {
            "path": record[
                "path"
            ],
            "markers": record[
                "placeholder_markers"
            ],
        }
        for record in auth_records
        if record[
            "placeholder_markers"
        ]
    ]

    repo_text = repository_text()

    snaptrade = detect_markers(
        (
            "\n".join(
                path.read_text(
                    encoding="utf-8",
                    errors="replace",
                ).lower()
                for path in python_files(
                    SNAPTRADE_ROOT
                )
            )
            if SNAPTRADE_ROOT.is_dir()
            else ""
        ),
        SNAPTRADE_MARKERS,
    )

    cerberus = cerberus_inventory(
        repo_text
    )

    auth_completeness = (
        implementation_percentage(
            auth_milestones
        )
    )

    snaptrade_completeness = (
        implementation_percentage(
            snaptrade
        )
    )

    no_auth_claim = (
        auth_completeness < 70.0
    )

    deployment_auth_blocker = bool(
        sensitive_unauthenticated
    )

    safe_deferred = (
        not fail_open_signals
        and not syntax_errors
        and not deployment_auth_blocker
    )

    if safe_deferred:
        auth_disposition = (
            "DEFERRED_BY_DESIGN_SAFE_DORMANT"
        )

    elif deployment_auth_blocker:
        auth_disposition = (
            "DEFERRED_BUT_DEPLOYMENT_BLOCKING"
        )

    else:
        auth_disposition = (
            "PARTIAL_REQUIRES_REMEDIATION"
        )

    auth_required_gates = [
        {
            "gate": "User profile database schema",
            "complete": auth_milestones[
                "user_profile_model"
            ][
                "detected"
            ],
        },
        {
            "gate": "User profile repository/service",
            "complete": auth_milestones[
                "user_repository"
            ][
                "detected"
            ],
        },
        {
            "gate": "Password or identity-provider boundary",
            "complete": auth_milestones[
                "password_hashing"
            ][
                "detected"
            ],
        },
        {
            "gate": "JWT access-token issuance",
            "complete": auth_milestones[
                "jwt_issue"
            ][
                "detected"
            ],
        },
        {
            "gate": "JWT verification and claim validation",
            "complete": auth_milestones[
                "jwt_verify"
            ][
                "detected"
            ],
        },
        {
            "gate": "Access-token expiry",
            "complete": auth_milestones[
                "access_token_expiry"
            ][
                "detected"
            ],
        },
        {
            "gate": "Refresh-token rotation",
            "complete": auth_milestones[
                "refresh_tokens"
            ][
                "detected"
            ],
        },
        {
            "gate": "Revocation and logout invalidation",
            "complete": auth_milestones[
                "token_revocation"
            ][
                "detected"
            ],
        },
        {
            "gate": "Session persistence",
            "complete": auth_milestones[
                "session_persistence"
            ][
                "detected"
            ],
        },
        {
            "gate": "Authentication rate limits",
            "complete": auth_milestones[
                "auth_rate_limits"
            ][
                "detected"
            ],
        },
        {
            "gate": "Token-fetch and connection timeouts",
            "complete": auth_milestones[
                "token_fetch_timeout"
            ][
                "detected"
            ],
        },
        {
            "gate": "Focused auth failure qualification",
            "complete": False,
        },
    ]

    snaptrade_required_gates = [
        {
            "gate": "Authentication identity available",
            "complete": (
                auth_completeness >= 80.0
            ),
        },
        {
            "gate": "Per-user broker identity mapping",
            "complete": snaptrade[
                "user_mapping"
            ][
                "detected"
            ],
        },
        {
            "gate": "Encrypted credential/token storage",
            "complete": snaptrade[
                "token_storage"
            ][
                "detected"
            ]
            and snaptrade[
                "secret_management"
            ][
                "detected"
            ],
        },
        {
            "gate": "Connection portal/OAuth flow",
            "complete": snaptrade[
                "connection_flow"
            ][
                "detected"
            ],
        },
        {
            "gate": "Timeout, retry and backoff policy",
            "complete": snaptrade[
                "timeout_retry"
            ][
                "detected"
            ],
        },
        {
            "gate": "Webhook signature verification",
            "complete": snaptrade[
                "webhook_verification"
            ][
                "detected"
            ],
        },
        {
            "gate": "Paper-only execution enforcement",
            "complete": snaptrade[
                "paper_only_guard"
            ][
                "detected"
            ],
        },
        {
            "gate": "Risk and kill-switch enforcement",
            "complete": snaptrade[
                "risk_gate"
            ][
                "detected"
            ],
        },
        {
            "gate": "Broker action audit logging",
            "complete": snaptrade[
                "audit_logging"
            ][
                "detected"
            ],
        },
        {
            "gate": "Cerberus external head qualified",
            "complete": False,
        },
        {
            "gate": "Cerberus internal head qualified",
            "complete": False,
        },
        {
            "gate": "Cerberus streaming head qualified",
            "complete": False,
        },
        {
            "gate": "SnapTrade sandbox qualification",
            "complete": False,
        },
    ]

    auth_remaining = sum(
        1
        for gate in auth_required_gates
        if not gate[
            "complete"
        ]
    )

    snaptrade_remaining = sum(
        1
        for gate in snaptrade_required_gates
        if not gate[
            "complete"
        ]
    )

    manifest = source_manifest()

    evidence = {
        "status": "completed",
        "generated_at": datetime.now(
            UTC
        ).isoformat(),
        "mode": "read_only",
        "auth_identity": {
            "files": auth_records,
            "placeholder_files": (
                placeholder_files
            ),
            "implementation_milestones": (
                auth_milestones
            ),
            "provisional_implementation_completeness": (
                auth_completeness
            ),
            "external_consumers": consumers,
            "production_consumer_count": len(
                production_consumers
            ),
            "fail_open_signals": (
                fail_open_signals
            ),
            "syntax_errors": syntax_errors,
        },
        "routes": {
            "route_files": routes,
            "potential_sensitive_unauthenticated": (
                sensitive_unauthenticated
            ),
        },
        "snaptrade": {
            "milestones": snaptrade,
            "provisional_implementation_completeness": (
                snaptrade_completeness
            ),
        },
        "cerberus": cerberus,
        "source_manifest": manifest,
        "source_modified": False,
        "database_modified": False,
    }

    EVIDENCE_JSON.write_text(
        json.dumps(
            evidence,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    report = {
        "campaign": (
            "NeuroVest Integrated "
            "Qualification Campaign"
        ),
        "batch": "IQC-REM-002",
        "batch_name": (
            "auth_identity Implementation-State "
            "Classification, Placeholder Boundary "
            "Qualification, and Security Roadmap Freeze"
        ),
        "status": "completed",
        "verified_at": datetime.now(
            UTC
        ).isoformat(),
        "mode": "read_only",
        "batch1_verified": True,
        "flow_baseline": {
            "backend_tests_passed": batch1[
                "whole_backend_tests"
            ][
                "passed"
            ],
            "backend_tests_failed": batch1[
                "whole_backend_tests"
            ][
                "failed"
            ],
            "unresolved_imports": 0,
            "dependency_cycles": 0,
        },
        "auth_identity": {
            "implementation_state": (
                "PARTIAL_PLACEHOLDER"
                if no_auth_claim
                else "IMPLEMENTED_UNQUALIFIED"
            ),
            "disposition": auth_disposition,
            "grade_impact": (
                "EXCLUDED_FROM_CURRENT_FLOW_QUALITY_SCORE"
            ),
            "production_authentication_available": False,
            "provisional_implementation_completeness": (
                auth_completeness
            ),
            "remaining_gate_count": auth_remaining,
            "required_gates": auth_required_gates,
            "safe_to_remain_deferred": (
                safe_deferred
            ),
            "deployment_blocker": (
                deployment_auth_blocker
            ),
            "fail_open_signals_detected": bool(
                fail_open_signals
            ),
        },
        "snaptrade": {
            "safe_connection_authorized": False,
            "provisional_implementation_completeness": (
                snaptrade_completeness
            ),
            "remaining_gate_count": (
                snaptrade_remaining
            ),
            "required_gates": (
                snaptrade_required_gates
            ),
        },
        "cerberus": cerberus,
        "recommended_sequence": [
            {
                "order": 1,
                "campaign": (
                    "Complete and qualify core application flows"
                ),
            },
            {
                "order": 2,
                "campaign": (
                    "Cerberus foundation: security event model, "
                    "telemetry boundary, and deny-by-default policy"
                ),
            },
            {
                "order": 3,
                "campaign": (
                    "Auth foundation: user profiles, identity "
                    "repository, JWT, expiry, refresh and revocation"
                ),
            },
            {
                "order": 4,
                "campaign": (
                    "Cerberus external and internal threat heads"
                ),
            },
            {
                "order": 5,
                "campaign": (
                    "SnapTrade read-only sandbox connection"
                ),
            },
            {
                "order": 6,
                "campaign": (
                    "Cerberus streaming threat head and "
                    "broker-stream qualification"
                ),
            },
            {
                "order": 7,
                "campaign": (
                    "Paper-only SnapTrade integration qualification"
                ),
            },
        ],
        "source_modified": False,
        "database_modified": False,
        "broker_execution_enabled": False,
        "live_trading_enabled": False,
        "next_step": (
            "IQC Remediation Batch 3 — chat_public "
            "Implementation-State and Boundary Qualification"
        ),
    }

    REPORT_JSON.write_text(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    report_hash = sha256_file(
        REPORT_JSON
    )

    evidence_hash = sha256_file(
        EVIDENCE_JSON
    )

    freeze = {
        "status": "frozen",
        "batch": "IQC-REM-002",
        "frozen_at": datetime.now(
            UTC
        ).isoformat(),
        "roadmap_report_sha256": (
            report_hash
        ),
        "evidence_report_sha256": (
            evidence_hash
        ),
        "source_manifest_sha256": (
            manifest[
                "manifest_sha256"
            ]
        ),
        "source_modified": False,
        "database_modified": False,
    }

    FREEZE_JSON.write_text(
        json.dumps(
            freeze,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    lines = [
        "=" * 92,
        "NEUROVEST INTEGRATED QUALIFICATION CAMPAIGN",
        (
            "IQC REMEDIATION BATCH 2 — AUTH_IDENTITY "
            "IMPLEMENTATION-STATE AND SECURITY ROADMAP"
        ),
        "=" * 92,
        "",
        "STATUS",
        "COMPLETE AND VERIFIED",
        "",
        "MODE",
        "READ ONLY",
        "",
        "FLOW BASELINE",
        (
            "Backend tests passed:            "
            f"{batch1['whole_backend_tests']['passed']}"
        ),
        "Backend tests failed:            0",
        "Unresolved imports:              0",
        "Dependency cycles:               0",
        "",
        "AUTH_IDENTITY DISPOSITION",
        (
            "Implementation state:           "
            f"{report['auth_identity']['implementation_state']}"
        ),
        (
            "Disposition:                    "
            f"{auth_disposition}"
        ),
        (
            "Estimated implementation found: "
            f"{auth_completeness:.1f}%"
        ),
        (
            "Remaining auth gates:           "
            f"{auth_remaining}"
        ),
        (
            "Safe to remain deferred:        "
            f"{'YES' if safe_deferred else 'NO'}"
        ),
        (
            "Deployment blocker today:       "
            f"{'YES' if deployment_auth_blocker else 'NO'}"
        ),
        (
            "Fail-open signals detected:     "
            f"{'YES' if fail_open_signals else 'NO'}"
        ),
        "Current flow-grade impact:        EXCLUDED",
        "",
        "SNAPTRADE READINESS",
        (
            "Estimated implementation found: "
            f"{snaptrade_completeness:.1f}%"
        ),
        (
            "Remaining safety gates:         "
            f"{snaptrade_remaining}"
        ),
        "Safe connection authorized:       NO",
        "",
        "CERBERUS SECURITY READINESS",
    ]

    for name, item in cerberus.items():
        lines.extend(
            [
                (
                    f"- {name}: "
                    f"{item['provisional_completeness']:.1f}%"
                ),
                (
                    f"  {item['description']}"
                ),
            ]
        )

    lines.extend(
        [
            "",
            "RECOMMENDED IMPLEMENTATION ORDER",
        ]
    )

    for item in report[
        "recommended_sequence"
    ]:
        lines.append(
            f"{item['order']}. "
            f"{item['campaign']}"
        )

    lines.extend(
        [
            "",
            "SAFETY",
            "- Production auth available: NO",
            "- SnapTrade connection authorized: NO",
            "- Broker execution enabled: NO",
            "- Live trading enabled: NO",
            "- Source modified: NO",
            "- Database modified: NO",
            "",
            "NEXT",
            (
                "IQC Remediation Batch 3 — chat_public "
                "Implementation-State and Boundary Qualification"
            ),
            "",
            "=" * 92,
        ]
    )

    rendered = (
        "\n".join(
            lines
        )
        + "\n"
    )

    REPORT_TEXT.write_text(
        rendered,
        encoding="utf-8",
    )

    print(rendered)

    print("Roadmap report:")
    print(REPORT_JSON)
    print()

    print("Evidence report:")
    print(EVIDENCE_JSON)
    print()

    print("Freeze manifest:")
    print(FREEZE_JSON)


if __name__ == "__main__":
    main()
