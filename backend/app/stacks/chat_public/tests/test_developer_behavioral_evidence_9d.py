
import hashlib
import json
from datetime import datetime, timedelta, timezone

from backend.app.stacks.chat_public import (
    developer_behavioral_evidence_v5 as behavior,
)

NAME = "test_developer_citations_v5.py"

def make_fixture(root):
    directory = (
        root / "backend/app/stacks/chat_public/tests"
    )
    directory.mkdir(parents=True)

    source = directory / NAME
    source.write_text("def test_sample(): assert True\n")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()

    report = root / behavior.REPORT
    report.parent.mkdir(parents=True)

    document = {
        "schema": behavior.SCHEMA,
        "status": "offline_regression",
        "observed_utc": datetime.now(timezone.utc).isoformat(),
        "exit_code": 0,
        "passed": 7,
        "tests": [{"name": NAME, "sha256": digest}],
    }
    report.write_text(json.dumps(document))
    return report, document, source

def test_valid_report(tmp_path):
    make_fixture(tmp_path)
    result = behavior.load_behavioral_evidence(tmp_path)
    assert result is not None
    assert result["passed"] == 7

def test_changed_test_rejected(tmp_path):
    _, _, source = make_fixture(tmp_path)
    source.write_text("def test_sample(): assert False\n")
    assert behavior.load_behavioral_evidence(tmp_path) is None

def test_expired_report_rejected(tmp_path):
    report, data, _ = make_fixture(tmp_path)
    data["observed_utc"] = (
        datetime.now(timezone.utc)
        - timedelta(days=10)
    ).isoformat()
    report.write_text(json.dumps(data))
    assert behavior.load_behavioral_evidence(tmp_path) is None

def test_failed_report_rejected(tmp_path):
    report, data, _ = make_fixture(tmp_path)
    data["exit_code"] = 1
    report.write_text(json.dumps(data))
    assert behavior.load_behavioral_evidence(tmp_path) is None

def test_unapproved_file_rejected(tmp_path):
    report, data, _ = make_fixture(tmp_path)
    data["tests"][0]["name"] = "secret_test.py"
    report.write_text(json.dumps(data))
    assert behavior.load_behavioral_evidence(tmp_path) is None

def test_grounded_improvement_brief(tmp_path):
    make_fixture(tmp_path)
    brief = behavior.behavioral_evidence_brief(
        tmp_path,
        "What do you need to improve?",
    )
    normalized = " ".join(brief.split())

    assert "Passing tests: 7" in normalized
    assert "Do not describe passing tests as failures" in normalized
    assert "not observed production deficiencies" in normalized
    assert "multi-turn tests" in normalized

def test_missing_report_is_safe(tmp_path):
    assert behavior.load_behavioral_evidence(tmp_path) is None
    assert behavior.behavioral_evidence_brief(
        tmp_path, "Improve"
    ) == ""
