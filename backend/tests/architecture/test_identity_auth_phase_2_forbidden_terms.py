from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STACK = ROOT / "app" / "stacks" / "identity_auth"

FORBIDDEN_TERMS = [
    "jwt.encode",
    "OAuth2PasswordBearer",
    "verify_password",
    "hash_password",
    "create_access_token",
    "login_user",
    "authenticate_user",
]


def test_identity_auth_phase_2_has_no_auth_implementation() -> None:
    scanned = []

    for path in STACK.rglob("*.py"):
        text = path.read_text(errors="ignore")
        scanned.append(path)

        for term in FORBIDDEN_TERMS:
            assert term not in text, f"Forbidden auth implementation term {term!r} found in {path}"

    assert scanned
