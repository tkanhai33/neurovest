from future import annotations

from pathlib import Path

ROOT = Path(file).resolve().parents[1]

CODEOWNERS = ROOT / ".github/CODEOWNERS"
PR_TEMPLATE = ROOT / ".github/pull_request_template.md"
SECURITY = ROOT / ".github/SECURITY.md"
CONTRIBUTING = ROOT / ".github/CONTRIBUTING.md"

def read(path: Path) -> str:
assert path.is_file(), f"Missing required file: {path}"

text = path.read_text(
    encoding="utf-8",
)

assert text.strip()

return text

def test_codeowners_covers_critical_boundaries() -> None:
text = read(CODEOWNERS)

required = {
    "* ",
    "/.github/",
    "/backend/app/main.py",
    "/backend/app/stacks/identity_auth/",
    "/backend/app/stacks/chat_public/",
    "/backend/app/stacks/wolfden_ai/",
    "/backend/app/stacks/risk/",
    "/backend/app/stacks/execution/",
    "/backend/app/stacks/snaptrade/",
    "/backend/app/stacks/journal_ledger/",
    "/frontend/app/admin/",
}

missing = sorted(
    value
    for value in required
    if value not in text
)

assert not missing, missing

ownership_lines = [
    line.strip()
    for line in text.splitlines()
    if (
        line.strip()
        and not line.lstrip().startswith("#")
    )
]

assert ownership_lines

for line in ownership_lines:
    parts = line.split()

    assert len(parts) >= 2

    assert all(
        owner.startswith("@")
        for owner in parts[1:]
    )

def test_pull_request_template_preserves_safety_boundaries() -> None:
text = read(PR_TEMPLATE).lower()

required = {
    "architecture boundary",
    "live brokerage",
    "autonomous",
    "risk gate",
    "authorization",
    "verification performed",
    "failure-path",
    "release disposition",
}

missing = sorted(
    value
    for value in required
    if value not in text
)

assert not missing, missing

def test_security_policy_covers_fintech_and_ai_risk() -> None:
text = read(SECURITY).lower()

required = {
    "authentication",
    "authorization",
    "live-versus-paper",
    "risk-gate",
    "order duplication",
    "ledger",
    "prompt injection",
    "private-data disclosure",
    "denial of service",
    "raw access or refresh tokens",
}

missing = sorted(
    value
    for value in required
    if value not in text
)

assert not missing, missing

def test_contributing_contract_is_architecture_first() -> None:
text = read(CONTRIBUTING).lower()

required = {
    "architecture-first",
    "duplicate services",
    "exact source and call shape",
    "archive affected files",
    "focused tests",
    "fail-closed",
    "git clean",
    "git reset --hard",
    "live brokerage",
    "ai autonomy",
}

missing = sorted(
    value
    for value in required
    if value not in text
)

assert not missing, missing
