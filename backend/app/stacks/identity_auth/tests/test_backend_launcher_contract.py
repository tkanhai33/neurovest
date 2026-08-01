from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]

LAUNCHER = (
    ROOT
    / "scripts"
    / "start_neurovest_backend.sh"
)


def test_backend_launcher_exists_and_is_executable() -> None:
    assert LAUNCHER.is_file()

    mode = LAUNCHER.stat().st_mode

    assert mode & 0o111


def test_backend_launcher_loads_local_ignored_jwt_environment() -> None:
    source = LAUNCHER.read_text(
        encoding="utf-8"
    )

    assert (
        "runtime/dev_auth/dev_jwt_env.sh"
        in source
    )

    assert (
        "runtime/dev_auth/"
        "dev_jwt_env.before_aiq003_20260727_124234.sh"
        in source
    )

    assert (
        'source "$JWT_ENV"'
        in source
    )

    assert (
        "NEUROVEST_JWT_SECRET"
        in source
    )


def test_backend_launcher_never_contains_secret_value() -> None:
    source = LAUNCHER.read_text(
        encoding="utf-8"
    )

    assert "JWT secret:" in source
    assert "PRESENT — REDACTED" in source

    for line in source.splitlines():
        stripped = line.strip()

        if not stripped.startswith(
            "NEUROVEST_JWT_SECRET="
        ):
            continue

        raise AssertionError(
            "Launcher must never contain a JWT secret value."
        )


def test_backend_launcher_uses_expected_application() -> None:
    source = LAUNCHER.read_text(
        encoding="utf-8"
    )

    assert "backend.app.main:app" in source
    assert "--host" in source
    assert "--port" in source
