#!/usr/bin/env python3
"""NeuroVest developer patch review, approval and rollback.

Initial scope: the developer repository inspection module.
No arbitrary command execution, no live trading, no database changes.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / "Neurovest"
PROPOSALS = ROOT / "runtime/developer_patch_proposals"
BACKUPS = ROOT / "runtime/developer_patch_backups"

ALLOWED = {
    "backend/app/stacks/chat_public/developer_repository_inspection.py": [
        "backend/app/stacks/chat_public/tests/"
        "test_developer_repository_inspection.py",
        "backend/app/stacks/chat_public/tests/"
        "test_developer_response_builder.py",
        "backend/app/stacks/chat_public/tests/"
        "test_developer_sensitive_filter_regression.py",
    ],
}

# NEUROVEST_PATCH_SCOPE_EXPANSION_V1
ALLOWED['backend/app/stacks/chat_public/developer_self_review.py'] = [
    'backend/app/stacks/chat_public/tests/test_developer_self_review.py',
    'backend/app/stacks/chat_public/tests/test_developer_self_review_ai.py',
]

HUNK = re.compile(
    r"^@@ -(\d+)(?:,(\d+))? "
    r"\+(\d+)(?:,(\d+))? @@"
)

def digest(data):
    return hashlib.sha256(data).hexdigest()


def resolve_proposal(value):
    path = Path(value).expanduser().resolve()

    if path.parent != PROPOSALS.resolve():
        raise ValueError(
            "Proposal must be an immediate child of "
            "runtime/developer_patch_proposals."
        )

    if not path.is_dir() or path.is_symlink():
        raise ValueError("Invalid proposal directory.")

    return path


def apply_unified_diff(original, diff, relative):
    before = original.splitlines(keepends=True)
    patch = diff.splitlines(keepends=True)

    if len(patch) < 3:
        raise ValueError("Invalid unified diff.")

    if patch[0].rstrip("\r\n") != "--- a/" + relative:
        raise ValueError("Unexpected old-file header.")

    if patch[1].rstrip("\r\n") != "+++ b/" + relative:
        raise ValueError("Unexpected new-file header.")

    result = []
    cursor = 0
    i = 2
    hunks = 0

    while i < len(patch):
        header = patch[i].rstrip("\r\n")
        match = HUNK.match(header)

        if not match:
            raise ValueError(
                "Unexpected unified-diff content."
            )

        old_start = int(match.group(1))
        old_count = int(match.group(2) or "1")
        new_count = int(match.group(4) or "1")

        target = old_start - 1 if old_count else old_start

        if target < cursor or target > len(before):
            raise ValueError("Invalid or overlapping hunk.")

        result.extend(before[cursor:target])
        cursor = target
        i += 1

        old_seen = 0
        new_seen = 0

        while i < len(patch) and not patch[i].startswith("@@ "):
            line = patch[i]
            kind = line[:1]
            content = line[1:]

            if kind == " ":
                if cursor >= len(before) or before[cursor] != content:
                    raise ValueError("Patch context mismatch.")
                result.append(content)
                cursor += 1
                old_seen += 1
                new_seen += 1

            elif kind == "-":
                if cursor >= len(before) or before[cursor] != content:
                    raise ValueError("Patch removal mismatch.")
                cursor += 1
                old_seen += 1

            elif kind == "+":
                result.append(content)
                new_seen += 1

            else:
                raise ValueError(
                    "Unsupported diff content or newline marker."
                )

            i += 1

        if old_seen != old_count or new_seen != new_count:
            raise ValueError("Diff hunk line counts do not match.")

        hunks += 1

    if hunks == 0:
        raise ValueError("No patch hunks found.")

    result.extend(before[cursor:])

    return "".join(result)


def load_and_validate(directory):
    meta_path = directory / "proposal.json"
    diff_path = directory / "change.diff"

    if not meta_path.is_file() or not diff_path.is_file():
        raise ValueError("Proposal files are missing.")

    if meta_path.is_symlink() or diff_path.is_symlink():
        raise ValueError("Proposal symlinks are prohibited.")

    metadata = json.loads(
        meta_path.read_text(encoding="utf-8")
    )

    if metadata.get("type") != "developer_patch_preview":
        raise ValueError("Unsupported proposal type.")

    if metadata.get("applied") is not False:
        raise ValueError("Proposal is not pending.")

    relative = metadata.get("source_file")

    if relative not in ALLOWED:
        raise ValueError(
            "Source is outside the initial approved developer scope."
        )

    source = ROOT / relative

    if source.is_symlink() or not source.is_file():
        raise ValueError("Invalid source file.")

    source_bytes = source.read_bytes()

    if digest(source_bytes) != metadata.get("source_sha256"):
        raise ValueError(
            "STALE_PROPOSAL: source SHA256 changed. "
            "Generate a new proposal."
        )

    original = source_bytes.decode("utf-8")

    diff = diff_path.read_text(encoding="utf-8")

    if len(diff) > 30000:
        raise ValueError("Diff exceeds size limit.")

    candidate = apply_unified_diff(
        original,
        diff,
        relative,
    )

    if candidate == original:
        raise ValueError("Patch makes no change.")

    ast.parse(candidate)

    # NEUROVEST_CHANGE_SCOPE_GUARD_V1
    scope_check = __import__('runpy').run_path(
        str(ROOT / 'scripts/neuro_developer_patch_scope.py')
    )['enforce_patch_scope']
    scope_check(
        original, candidate, metadata.get('task')
    )

    candidate_bytes = candidate.encode("utf-8")

    if digest(candidate_bytes) != metadata.get("candidate_sha256"):
        raise ValueError(
            "Candidate hash mismatch. "
            "Proposal is incomplete or altered."
        )

    return metadata, source, source_bytes, candidate_bytes


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--proposal",
        required=True,
        help="Exact proposal directory",
    )

    parser.add_argument(
        "--approve",
        action="store_true",
        help="Explicitly apply this proposal and run focused tests",
    )

    args = parser.parse_args()
    directory = resolve_proposal(args.proposal)

    metadata, source, original, candidate = load_and_validate(
        directory
    )

    print("=" * 72)
    print("NEUROVEST — DEVELOPER PATCH APPLICATION")
    print("=" * 72)

    print("PROPOSAL=", directory.name)
    print("SOURCE=", metadata["source_file"])
    print("MODEL=", metadata.get("model"))
    print("TASK=", metadata.get("task"))
    print("SOURCE_SHA256=", digest(original))
    print("CANDIDATE_SHA256=", digest(candidate))

    if not args.approve:
        print()
        print("PATCH_VALIDATION=PASS")
        print("PYTHON_SYNTAX=PASS")
        print("SOURCE_HASH=PASS")
        print("CANDIDATE_HASH=PASS")
        print("PATCH_APPLIED=False")
        print("TESTS_EXECUTED=False")
        print("MODE=DRY_RUN")
        print()
        print(
            "This preview does not establish that the "
            "proposed change solves the requested problem."
        )
        return

    stamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    backup_dir = BACKUPS / (
        f"application_{stamp}_{os.getpid()}"
    )

    backup_dir.mkdir(
        parents=True,
        mode=0o700,
        exist_ok=False,
    )

    backup_file = backup_dir / "original.py"
    backup_file.write_bytes(original)

    print()
    print("EXPLICIT_APPROVAL=True")
    print("BACKUP=", backup_file)

    # Recheck the source immediately before applying.
    if source.read_bytes() != original:
        raise RuntimeError(
            "Source changed after validation. "
            "Application cancelled."
        )

    applied = False

    try:
        # Exclusive creation prevents overwriting an unrelated temp file.
        temporary = source.with_name(
            source.name + f".neuro_patch_{os.getpid()}"
        )

        fd = os.open(
            temporary,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )

        try:
            with os.fdopen(fd, "wb") as output:
                output.write(candidate)

            shutil.copymode(source, temporary)
            os.replace(temporary, source)
            applied = True

        finally:
            if temporary.exists():
                temporary.unlink()

        print("PATCH_APPLIED=True")
        print()
        print("=== FOCUSED TESTS ===", flush=True)

        tests = ALLOWED[metadata["source_file"]]

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                *tests,
            ],
            cwd=ROOT,
            env={
                **os.environ,
                "PYTHONDONTWRITEBYTECODE": "1",
            },
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )

        print(result.stdout[-7000:])

        if result.stderr:
            print(result.stderr[-1500:])

        if result.returncode != 0:
            raise RuntimeError(
                f"Focused tests failed: {result.returncode}"
            )

        if source.read_bytes() != candidate:
            raise RuntimeError(
                "Source changed unexpectedly after tests."
            )

        metadata["applied"] = True
        metadata["tests_executed"] = True
        metadata["tests_passed"] = True
        metadata["applied_at"] = datetime.now(
            timezone.utc
        ).isoformat()
        metadata["backup_path"] = str(backup_file)

        (directory / "proposal.json").write_text(
            json.dumps(metadata, indent=2),
            encoding="utf-8",
        )

        print()
        print("FOCUSED_TESTS=PASS")
        print("SOURCE_CHANGES_RETAINED=True")
        print("BACKUP_AVAILABLE=True")
        print("BACKEND_RESTARTED=False")

    except BaseException:
        if applied:
            if source.read_bytes() == candidate:
                source.write_bytes(original)
                print("AUTOMATIC_ROLLBACK=COMPLETE")
            else:
                print(
                    "AUTOMATIC_ROLLBACK=BLOCKED_BY_CONCURRENT_EDIT"
                )
                print("ORIGINAL_BACKUP=", backup_file)
        raise


if __name__ == "__main__":
    try:
        main()

    except Exception as exc:
        print()
        print(
            "PATCH_APPLICATION_ERROR=",
            type(exc).__name__,
            str(exc)[:700],
        )
        print("BACKEND_RESTARTED=False")
        sys.exit(1)

    finally:
        print("Terminal remains open.")
