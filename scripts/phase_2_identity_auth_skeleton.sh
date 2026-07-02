#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$ROOT/backend"
STACK="$BACKEND/app/stacks/identity_auth"

echo "========================================="
echo "PHASE 2 - IDENTITY / AUTH SKELETON"
echo "========================================="

cd "$ROOT"

echo "Running baseline tests..."
pytest

mkdir -p "$STACK"/{contracts,domain,services,adapters,api,tests}

cat > "$STACK/contracts/identity_contract.py" <<'EOF'
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class UserRole(StrEnum):
    USER = "user"
    ADMIN = "admin"
    DEVELOPER = "developer"


class AccountStatus(StrEnum):
    ACTIVE = "active"
    DISABLED = "disabled"


@dataclass(frozen=True)
class IdentityUserContract:
    id: str
    email: str
    role: UserRole
    status: AccountStatus


@dataclass(frozen=True)
class IdentityAuthSkeletonStatus:
    stack: str = "identity_auth"
    phase: str = "phase_2_skeleton"
    login_implemented: bool = False
    jwt_implemented: bool = False
    password_auth_implemented: bool = False
    business_logic_implemented: bool = False
EOF

cat > "$STACK/domain/README.md" <<'EOF'
# Identity/Auth Domain

Phase 2 skeleton only.

Allowed:
- identity contracts
- model placeholders
- role/status enums
- testable skeleton status

Forbidden:
- login implementation
- password hashing
- JWT issuance
- permission enforcement logic
- session persistence logic
EOF

cat > "$STACK/services/identity_auth_service.py" <<'EOF'
from __future__ import annotations

from app.stacks.identity_auth.contracts.identity_contract import (
    IdentityAuthSkeletonStatus,
)


def get_identity_auth_skeleton_status() -> IdentityAuthSkeletonStatus:
    return IdentityAuthSkeletonStatus()
EOF

cat > "$STACK/api/identity_auth_routes.py" <<'EOF'
from __future__ import annotations

from fastapi import APIRouter

from app.stacks.identity_auth.services.identity_auth_service import (
    get_identity_auth_skeleton_status,
)

router = APIRouter(prefix="/identity-auth", tags=["identity-auth"])


@router.get("/status")
def identity_auth_status() -> dict[str, object]:
    status = get_identity_auth_skeleton_status()
    return {
        "stack": status.stack,
        "phase": status.phase,
        "login_implemented": status.login_implemented,
        "jwt_implemented": status.jwt_implemented,
        "password_auth_implemented": status.password_auth_implemented,
        "business_logic_implemented": status.business_logic_implemented,
    }
EOF

cat > "$STACK/adapters/README.md" <<'EOF'
# Identity/Auth Adapters

Phase 2 skeleton only.

No external auth providers.
No OAuth.
No broker identity integration.
EOF

cat > "$STACK/tests/README.md" <<'EOF'
# Identity/Auth Stack Tests

Phase 2 uses root backend tests for certification.
EOF

cat > "$STACK/README.md" <<'EOF'
# identity_auth

Phase 2 — Identity / Authentication Skeleton.

Owns:
- user identity contracts
- role/status definitions
- auth stack status interface

Forbidden in Phase 2:
- login implementation
- JWT issuance
- password auth
- permission enforcement logic
- frontend implementation
- broker access
EOF

cat > "$BACKEND/tests/contracts/test_identity_auth_contract.py" <<'EOF'
from app.stacks.identity_auth.contracts.identity_contract import (
    AccountStatus,
    IdentityAuthSkeletonStatus,
    IdentityUserContract,
    UserRole,
)


def test_identity_user_contract_shape() -> None:
    user = IdentityUserContract(
        id="user_001",
        email="test@example.com",
        role=UserRole.USER,
        status=AccountStatus.ACTIVE,
    )

    assert user.id == "user_001"
    assert user.email == "test@example.com"
    assert user.role == UserRole.USER
    assert user.status == AccountStatus.ACTIVE


def test_identity_auth_skeleton_has_no_real_auth() -> None:
    status = IdentityAuthSkeletonStatus()

    assert status.stack == "identity_auth"
    assert status.phase == "phase_2_skeleton"
    assert status.login_implemented is False
    assert status.jwt_implemented is False
    assert status.password_auth_implemented is False
    assert status.business_logic_implemented is False
EOF

cat > "$BACKEND/tests/smoke/test_identity_auth_status.py" <<'EOF'
from app.stacks.identity_auth.services.identity_auth_service import (
    get_identity_auth_skeleton_status,
)


def test_identity_auth_status_is_skeleton_only() -> None:
    status = get_identity_auth_skeleton_status()

    assert status.stack == "identity_auth"
    assert status.phase == "phase_2_skeleton"
    assert status.login_implemented is False
    assert status.jwt_implemented is False
    assert status.password_auth_implemented is False
    assert status.business_logic_implemented is False
EOF

cat > "$BACKEND/tests/architecture/test_identity_auth_phase_2_forbidden_terms.py" <<'EOF'
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
EOF

cat > "$ROOT/docs/contracts/PHASE_2_IDENTITY_AUTH_SKELETON_CONTRACT.md" <<'EOF'
# Phase 2 Identity / Authentication Skeleton Contract

## Status

Phase 2 skeleton only.

## Purpose

Create the identity/auth stack shape without implementing real authentication.

## Allowed

- identity user contract
- role enum
- account status enum
- skeleton status service
- API placeholder
- tests
- certification artifact

## Forbidden

- login implementation
- JWT issuance
- password hashing
- OAuth implementation
- permission enforcement logic
- frontend implementation
- broker integration
- business logic

## Exit Criteria

- tests pass
- identity_auth stack has contracts/services/api placeholders
- no real auth implementation exists
- safety locks remain intact
EOF

cat > "$ROOT/certification/phase_01/PHASE_2_IDENTITY_AUTH_SKELETON_CERTIFICATION.md" <<'EOF'
# Phase 2 Identity / Authentication Skeleton Certification

Status: pending

Checks:
- identity_auth contract exists
- skeleton service exists
- API placeholder exists
- no login implementation
- no JWT implementation
- no password auth implementation
- tests pass
EOF

echo
echo "Running Phase 2 tests..."
pytest

cat > "$ROOT/certification/phase_01/PHASE_2_IDENTITY_AUTH_SKELETON_CERTIFICATION.md" <<'EOF'
# Phase 2 Identity / Authentication Skeleton Certification

Status: PASS

Checks:
- identity_auth contract exists
- skeleton service exists
- API placeholder exists
- no login implementation
- no JWT implementation
- no password auth implementation
- tests pass

Result:
- Phase 2 identity/auth skeleton is certified.
EOF

echo
echo "========================================="
echo "PHASE 2 COMPLETE"
echo "========================================="
echo "PASS: Identity/Auth skeleton created and certified."
