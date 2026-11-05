
"""Offline developer behavioral evidence.

Test results are observations, not proof of production
readiness, global conversational accuracy or live trading.
"""

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "neurovest_v5_behavioral_evidence_v1"

REPORT = (
    "runtime/qualification/"
    "neuro_v5_behavioral_evidence_v1.json"
)

ALLOWED = {
    "test_developer_conversation_quality_9b.py",
    "test_developer_explanatory_fallback_9c_r3.py",
    "test_developer_citations_v5.py",
    "test_developer_model_synthesis_v5.py",
    "test_developer_awareness_integration_v5.py",
    "test_developer_v5_integrated_execution.py",
}

def load_behavioral_evidence(root):
    root = Path(root).resolve()
    path = root / REPORT

    if (
        path.is_symlink()
        or not path.is_file()
        or not path.resolve().is_relative_to(root)
    ):
        return None

    try:
        if path.stat().st_size > 16384:
            return None

        data = json.loads(path.read_text("utf-8"))

        if not isinstance(data, dict):
            return None

        if (
            data.get("schema") != SCHEMA
            or data.get("status") != "offline_regression"
            or data.get("exit_code") != 0
        ):
            return None

        value = data.get("observed_utc")

        if not isinstance(value, str):
            return None

        stamp = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )

        if stamp.tzinfo is None:
            return None

        age = (
            datetime.now(timezone.utc)
            - stamp.astimezone(timezone.utc)
        ).total_seconds()

        if age < -300 or age > 604800:
            return None

        passed = data.get("passed")

        if (
            isinstance(passed, bool)
            or not isinstance(passed, int)
            or not 1 <= passed <= 100000
        ):
            return None

        records = data.get("tests")

        if (
            not isinstance(records, list)
            or not 1 <= len(records) <= len(ALLOWED)
        ):
            return None

        seen = set()

        for entry in records:
            if not isinstance(entry, dict):
                return None

            name = entry.get("name")
            digest = entry.get("sha256")

            if (
                not isinstance(name, str)
                or name not in ALLOWED
                or name in seen
                or not isinstance(digest, str)
                or re.fullmatch(
                    r"[0-9a-f]{64}", digest
                ) is None
            ):
                return None

            path = (
                root
                / "backend/app/stacks/chat_public/tests"
                / name
            )

            if (
                path.is_symlink()
                or not path.is_file()
                or not path.resolve().is_relative_to(root)
            ):
                return None

            actual = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()

            if actual != digest:
                return None

            seen.add(name)

        return {
            "passed": passed,
            "observed_utc": stamp.isoformat(),
            "tests": sorted(seen),
        }

    except (
        OSError,
        ValueError,
        TypeError,
        OverflowError,
        UnicodeError,
    ):
        return None

def behavioral_evidence_brief(root, question):
    observed = load_behavioral_evidence(root)

    if observed is None:
        return ""

    lines = [
        "",
        "",
        "VERIFIED OFFLINE BEHAVIORAL OBSERVATIONS:",
        "Evidence: completed local regression tests.",
        "Observed UTC: " + observed["observed_utc"],
        "Passing tests: " + str(observed["passed"]),
        "Test files: " + ", ".join(observed["tests"]),
        "",
        "These are isolated test observations, not",
        "proof of production reliability, general",
        "conversational intelligence, runtime latency,",
        "or live broker readiness.",
        "Do not use test filenames as source citations.",
    ]

    q = str(question or "").casefold()

    if any(x in q for x in (
        "improve", "limitation", "priority",
        "weakness", "roadmap", "need to",
    )):
        lines.extend([
            "",
            "IMPROVEMENT PRIORITIZATION:",
            "Do not describe passing tests as failures.",
            "The available observations establish",
            "specific successful offline regression checks.",
            "They do not measure general conversational",
            "quality, context retention or user outcomes.",
            "Propose controlled answer-quality evaluations,",
            "multi-turn tests, citation-to-claim checks,",
            "and measurable failure analysis.",
            "These are proposed evaluations, not",
            "observed production deficiencies.",
            "Rank specific changes after collecting",
            "actual failure or shortfall evidence.",
        ])

    return "\n".join(lines)
