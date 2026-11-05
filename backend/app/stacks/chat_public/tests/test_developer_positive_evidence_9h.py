
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from backend.app.stacks.chat_public import (
    developer_positive_evidence_v5 as positive,
)
from backend.app.stacks.chat_public import (
    developer_behavioral_evidence_v5 as behavioral,
)

def fixture_report(root):
    directory = (
        root / "backend/app/stacks/chat_public/tests"
    )
    directory.mkdir(parents=True)

    name = "test_developer_citations_v5.py"
    source = directory / name
    source.write_text(
        "def test_example(): assert True\n",
        encoding="utf-8",
    )

    document = {
        "schema": behavioral.SCHEMA,
        "status": "offline_regression",
        "observed_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "exit_code": 0,
        "passed": 7,
        "tests": [{
            "name": name,
            "sha256": hashlib.sha256(
                source.read_bytes()
            ).hexdigest(),
        }],
    }

    report = root / behavioral.REPORT
    report.parent.mkdir(parents=True)
    report.write_text(json.dumps(document), encoding="utf-8")

    return report, source

def test_positive_evidence_constructed(tmp_path):
    fixture_report(tmp_path)
    bundle = positive.build_positive_observations(tmp_path)

    assert bundle is not None
    assert bundle["passing_tests"] == 7
    assert len(bundle["observations"]) == 1
    assert bundle["observations"][0]["id"] == (
        "NV9H-CITATION_VALIDATION"
    )

def test_source_fingerprint_bound(tmp_path):
    _, source = fixture_report(tmp_path)
    source.write_text("changed", encoding="utf-8")
    assert positive.build_positive_observations(tmp_path) is None

def test_report_fingerprint_bound(tmp_path):
    report, _ = fixture_report(tmp_path)
    bundle = positive.build_positive_observations(tmp_path)

    assert bundle["report_sha256"] == hashlib.sha256(
        report.read_bytes()
    ).hexdigest()

def test_missing_report_no_claims(tmp_path):
    assert positive.build_positive_observations(tmp_path) is None
    assert positive.positive_evidence_brief(
        tmp_path, "What needs improvement?"
    ) == ""

def test_supported_conclusion_is_bounded(tmp_path):
    fixture_report(tmp_path)
    brief = positive.positive_evidence_brief(
        tmp_path, "What has been tested?"
    )

    assert "NV9H-CITATION_VALIDATION" in brief
    assert "Passing tests in the reported suite: 7" in brief
    assert "test filename does not establish" in brief.lower()
    assert "No production reliability" in brief

def test_priorities_are_evidence_gaps(tmp_path):
    fixture_report(tmp_path)
    brief = positive.positive_evidence_brief(
        tmp_path, "Neuro, what do you need to improve?"
    )

    assert "EVIDENCE-GROUNDED RECOMMENDATIONS" in brief
    assert "Priority 1" in brief
    assert "Priority 2" in brief
    assert "Priority 3" in brief
    assert "measurement gap" in brief
    assert "not a verified production failure" in brief

def test_report_with_failed_exit_rejected(tmp_path):
    report, _ = fixture_report(tmp_path)
    data = json.loads(report.read_text("utf-8"))
    data["exit_code"] = 1
    report.write_text(json.dumps(data), encoding="utf-8")

    assert positive.build_positive_observations(tmp_path) is None
