from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

SCHEMA = "neurovest.capability_evidence_registry.v1"

SAFE_KEYS = frozenset({
    "conversation_continuity_r2",
    "developer_self_assessment",
    "developer_role_authorization",
    "runtime_execution_observation",
    "qualification_gap_detection",
})

CAPABILITY_NAMES = {
    "conversation_continuity_r2": "Conversation continuity",
    "developer_self_assessment": "Evidence-grounded self-assessment",
    "developer_role_authorization": "Developer authorization",
    "runtime_execution_observation": "Runtime evidence observation",
    "qualification_gap_detection": "Qualification gap detection",
}

ACTIONS = {
    "developer_self_assessment":
        "Qualify the developer-only improvement-answer path.",
    "qualification_gap_detection":
        "Validate and connect a read-only evidence adapter.",
    "runtime_execution_observation":
        "Qualify bounded trace correlation and sanitization.",
    "developer_role_authorization":
        "Test anonymous, user, and verified-developer boundaries.",
    "conversation_continuity_r2":
        "Expand multi-turn behavioral regressions.",
}

PRIORITY_ORDER = (
    "developer_self_assessment",
    "qualification_gap_detection",
    "runtime_execution_observation",
    "developer_role_authorization",
    "conversation_continuity_r2",
)

class EvidenceError(ValueError):
    pass


def load_registry(path: Path, root: Path) -> dict:
    path = Path(path).resolve(strict=True)
    root = Path(root).resolve(strict=True)

    if not path.is_relative_to(root / "runtime" / "qualification"):
        raise EvidenceError("Registry outside qualification boundary")

    if not path.is_file() or path.stat().st_size > 2_000_000:
        raise EvidenceError("Registry size or type invalid")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise EvidenceError("Malformed registry") from exc

    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        raise EvidenceError("Unsupported evidence schema")

    if data.get("evidence_rules", {}).get(
        "live_broker_execution_approved"
    ) is not False:
        raise EvidenceError("Broker boundary not explicitly locked")

    if data.get("evidence_rules", {}).get(
        "developer_authorization_required"
    ) is not True:
        raise EvidenceError("Developer authorization requirement missing")

    for key in ("sources", "reports", "capabilities", "runtime"):
        if not isinstance(data.get(key), dict):
            raise EvidenceError("Required evidence section missing")

    if set(data["capabilities"]) != SAFE_KEYS:
        raise EvidenceError("Unexpected capability inventory")

    return data


def verify_source(root: Path, record: dict) -> bool:
    relative = record.get("path")
    expected = record.get("sha256")

    if not isinstance(relative, str) or not isinstance(expected, str):
        return False

    if not re.fullmatch(r"[0-9a-f]{64}", expected):
        return False

    base = (Path(root) / "backend").resolve(strict=True)
    target = (Path(root) / relative).resolve()

    if not target.is_relative_to(base):
        return False

    if not target.is_file() or target.is_symlink():
        return False

    return hashlib.sha256(target.read_bytes()).hexdigest() == expected


def classify(registry: dict, root: Path) -> dict:
    sources = registry["sources"]

    verified = {
        key: verify_source(root, record)
        for key, record in sources.items()
    }

    report = registry["reports"].get("referent_r2_behavior", {})
    regression = registry.get("regression", {})
    continuity = registry["capabilities"]["conversation_continuity_r2"]

    continuity_qualified = all((
        verified.get("context_assembler_r2", False),
        verified.get("chat_runtime", False),
        verified.get("relevant_history", False),
        report.get("decision_matches") is True,
        report.get("candidate_sha256")
            == sources.get("context_assembler_r2", {}).get("sha256"),
        report.get("context_cases_total") == 7,
        report.get("context_cases_passed") == 7,
        report.get("handler_pass") is True,
        report.get("fast_model_result") == "PASS",
        regression.get("qualified") is True,
        continuity.get("behavioral_qualification") is True,
    ))

    # Staged/offline evidence never grants production approval.
    result = {}

    source_map = {
        "conversation_continuity_r2": "context_assembler_r2",
        "developer_self_assessment": "developer_intelligence",
        "developer_role_authorization": "developer_role_guard",
        "runtime_execution_observation": "developer_execution_trace",
    }

    for key in PRIORITY_ORDER:
        source_key = source_map.get(key)

        if source_key:
            source_verified = verified.get(source_key, False)
        else:
            source_verified = (
                registry["capabilities"][key].get(
                    "evidence_registry_created"
                ) is True
            )

        qualified = (
            continuity_qualified
            if key == "conversation_continuity_r2"
            else False
        )

        result[key] = {
            "name": CAPABILITY_NAMES[key],
            "source_verified": source_verified,
            "behavioral_qualified": qualified,
            "production_approved": False,
            "production_approval_evidence": "not_established",
            "status": (
                "behaviorally_qualified"
                if qualified
                else "source_found_unqualified"
                if source_verified
                else "insufficient_evidence"
            ),
            "recommended_validation": ACTIONS[key],
        }

    return result


def generate_assessment(
    classifications: dict,
    *,
    verified_developer: bool,
) -> dict:
    if type(verified_developer) is not bool:
        raise EvidenceError("Developer status must be a verified boolean")

    if not verified_developer:
        return {
            "status": "denied",
            "reason": "verified_developer_required",
            "recommendations": [],
            "answer": "Developer diagnostics require verified authorization.",
        }

    recommendations = []

    for rank, key in enumerate(PRIORITY_ORDER, 1):
        record = classifications[key]

        recommendations.append({
            "rank": rank,
            "capability_id": key,
            "status": record["status"],
            "source_verified": record["source_verified"],
            "behavioral_qualified": record["behavioral_qualified"],
            "production_approved": False,
            "next_validation": record["recommended_validation"],
        })

    lines = [
        "NeuroVest — Evidence-grounded improvement assessment",
        "These are validation priorities, not autonomous changes.",
        "",
    ]

    for item in recommendations:
        lines.append(
            f"{item['rank']}. "
            f"{CAPABILITY_NAMES[item['capability_id']]}: "
            f"{item['status']}."
        )
        lines.append(f"   Next: {item['next_validation']}")

    lines.extend([
        "",
        "Evidence is bounded to the supplied offline registry.",
        "Unverified capabilities remain unqualified.",
        "No production approval is inferred.",
        "Developer authorization is required for changes.",
        "Live broker trading remains unapproved.",
    ])

    return {
        "status": "ok",
        "recommendations": recommendations,
        "answer": "\n".join(lines),
    }
