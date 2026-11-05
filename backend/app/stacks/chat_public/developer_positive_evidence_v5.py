
"""Positive, bounded developer evidence for V5.

Read only an already validated offline regression report.
Never infer production performance or test-case success from
a collection-level passing count.
"""

import hashlib
import json
from pathlib import Path

from backend.app.stacks.chat_public.developer_behavioral_evidence_v5 import (
    load_behavioral_evidence,
    REPORT,
)

SCHEMA = "neurovest_v5_positive_evidence_v1"

DOMAINS = (
    (
        "citation_validation",
        "test_developer_citations_v5.py",
        "Citation-related regression tests were included "
        "in a passing offline suite.",
    ),
    (
        "model_synthesis",
        "test_developer_model_synthesis_v5.py",
        "Developer synthesis regression tests were included "
        "in a passing offline suite.",
    ),
    (
        "developer_routing",
        "test_developer_awareness_integration_v5.py",
        "Developer integration regression tests were included "
        "in a passing offline suite.",
    ),
    (
        "integration_execution",
        "test_developer_v5_integrated_execution.py",
        "Controlled V5 execution tests were included "
        "in a passing offline suite.",
    ),
    (
        "conversation_guidance",
        "test_developer_conversation_quality_9b.py",
        "Conversation-guidance regression tests were included "
        "in a passing offline suite.",
    ),
    (
        "explanatory_fallback",
        "test_developer_explanatory_fallback_9c_r3.py",
        "Grounded fallback regression tests were included "
        "in a passing offline suite.",
    ),
)

def build_positive_observations(root):
    """Return verified suite observations with bounded claims."""
    root = Path(root).resolve()

    validated = load_behavioral_evidence(root)
    if validated is None:
        return None

    report_path = root / REPORT
    try:
        raw = report_path.read_bytes()
        report = json.loads(raw)

        if not isinstance(report, dict):
            return None

        if report.get("schema") != (
            "neurovest_v5_behavioral_evidence_v1"
        ):
            return None

        names = set(validated["tests"])
        report_hash = hashlib.sha256(raw).hexdigest()

        observations = []

        for key, filename, conclusion in DOMAINS:
            if filename not in names:
                continue

            observations.append({
                "id": "NV9H-" + key.upper(),
                "type": "offline_regression_inclusion",
                "source_test": filename,
                "conclusion": conclusion,
                "limitation": (
                    "This is a collection-level suite result. "
                    "It does not independently verify every "
                    "assertion in that file or establish "
                    "production behavior."
                ),
            })

        if not observations:
            return None

        return {
            "schema": SCHEMA,
            "status": "verified_offline_observations",
            "observed_utc": validated["observed_utc"],
            "report_sha256": report_hash,
            "passing_tests": validated["passed"],
            "observations": observations,
        }

    except (
        OSError, ValueError, TypeError,
        UnicodeError, KeyError,
    ):
        return None

def positive_evidence_brief(root, question):
    """Natural-language evidence and priorities for the dev model."""
    bundle = build_positive_observations(root)

    if bundle is None:
        return ""

    lines = [
        "",
        "",
        "STRUCTURED VERIFIED OFFLINE EVIDENCE:",
        "Evidence report SHA-256: " + bundle["report_sha256"],
        "Observed UTC: " + bundle["observed_utc"],
        "Passing tests in the reported suite: "
        + str(bundle["passing_tests"]),
        "These observations come from validated local "
        "test-report metadata, not source-line citations.",
        "",
        "Supported observations:",
    ]

    for observation in bundle["observations"]:
        lines.append(
            "- [" + observation["id"] + "] "
            + observation["conclusion"]
            + " Test file: "
            + observation["source_test"]
        )

    lines.extend([
        "",
        "EVIDENCE BOUNDARIES:",
        "A passing suite demonstrates only that the "
        "reported offline test execution passed.",
        "A test filename does not establish which "
        "individual cases ran or what behavior occurred.",
        "No production reliability, general intelligence, "
        "financial accuracy, or live broker execution "
        "is proven by this report.",
        "Evidence IDs are report identifiers, not "
        "allowed Python source citations.",
    ])

    q = str(question or "").casefold()

    if any(term in q for term in (
        "improve", "improvement", "priority",
        "priorities", "weakness", "limitation",
        "next", "roadmap", "need to",
        "evidence", "demonstrated", "tested",
    )):
        lines.extend([
            "",
            "EVIDENCE-GROUNDED RECOMMENDATIONS:",
            "Priority 1 - Measure ordinary conversation "
            "quality with representative multi-turn "
            "questions, expected outcomes, and observed "
            "answers. This is a measurement gap, not "
            "a verified production failure.",
            "Priority 2 - Evaluate financial explanations "
            "with controlled numerical cases and "
            "claim-to-evidence checks. Do not infer "
            "financial correctness from developer tests.",
            "Priority 3 - Collect per-case outcomes and "
            "failure categories so future improvements "
            "can be ranked by observed impact.",
            "No numeric accuracy score, defect rate or "
            "performance ranking is currently established "
            "by these observations.",
        ])

    return "\n".join(lines)
