#!/usr/bin/env python3
"""NeuroVest immutable repository snapshot publisher v1.

Publishes a verified copy of the existing inventory and graphs.
Does not rescan, update application source, or switch legacy readers.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "runtime/qualification/repository_intelligence_v1"
GENERATIONS = DATA / "generations"
CURRENT = DATA / "current"
LOCK = DATA / "snapshot_publish.lock"

NAMES = (
    "inventory.json",
    "dependency_graph.json",
    "dependency_graph_v2.json",
)

MAX_BYTES = 20_000_000
NAME_PATTERN = re.compile(
    r"^generation_[0-9]{8}T[0-9]{6}_[0-9a-f]{12}$"
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_limited(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ValueError("UNSAFE_OR_MISSING_ARTIFACT")

    if path.stat().st_size > MAX_BYTES:
        raise ValueError("ARTIFACT_SIZE_LIMIT")

    data = path.read_bytes()

    if len(data) > MAX_BYTES:
        raise ValueError("ARTIFACT_SIZE_LIMIT")

    return data


def validate(blobs: dict[str, bytes]) -> dict:
    inventory = json.loads(blobs["inventory.json"])
    graph1 = json.loads(blobs["dependency_graph.json"])
    graph2 = json.loads(blobs["dependency_graph_v2.json"])

    if inventory.get("schema") != "neurovest.repository_intelligence.v1":
        raise ValueError("INVENTORY_SCHEMA")

    if graph1.get("schema") != "neurovest.repository_dependency_graph.v1":
        raise ValueError("GRAPH_V1_SCHEMA")

    if graph2.get("schema") != "neurovest.repository_dependency_graph.v2":
        raise ValueError("GRAPH_V2_SCHEMA")

    inventory_hash = digest(blobs["inventory.json"])
    graph1_hash = digest(blobs["dependency_graph.json"])

    if graph1.get("inventory_sha256") != inventory_hash:
        raise ValueError("GRAPH_V1_STALE")

    if graph2.get("inventory_sha256") != inventory_hash:
        raise ValueError("GRAPH_V2_STALE")

    if graph2.get("graph_v1_sha256") != graph1_hash:
        raise ValueError("GRAPH_CHAIN_BROKEN")

    files = inventory.get("files")
    edges = graph2.get("resolved_file_edges")
    stacks = inventory.get("backend_stacks")

    if not isinstance(files, list) or not isinstance(edges, list):
        raise ValueError("INVALID_STRUCTURE")

    if not isinstance(stacks, dict):
        raise ValueError("INVALID_STACK_DATA")

    if not (
        0 < len(files) <= 30000
        and len(edges) <= 100000
        and len(stacks) <= 200
    ):
        raise ValueError("STRUCTURAL_LIMIT")

    if graph2.get("files_indexed") != len(files):
        raise ValueError("FILE_COUNT_MISMATCH")

    paths = {
        item.get("path")
        for item in files
        if isinstance(item, dict)
        and isinstance(item.get("path"), str)
    }

    if len(paths) != len(files):
        raise ValueError("DUPLICATE_OR_INVALID_FILES")

    for edge in edges:
        if (
            not isinstance(edge, dict)
            or edge.get("source") not in paths
            or edge.get("destination") not in paths
        ):
            raise ValueError("INVALID_DEPENDENCY_EDGE")

    return {
        "source_files": len(files),
        "file_edges": len(edges),
        "backend_stacks": len(stacks),
        "cross_stack_relationships": len(
            graph2.get("cross_stack_dependencies", [])
        ),
    }


def verify_generation(directory: Path) -> dict:
    blobs = {
        name: read_limited(directory / name)
        for name in NAMES
    }

    manifest = json.loads(
        read_limited(directory / "manifest.json")
    )

    if manifest.get("schema") != "neurovest.snapshot.v1":
        raise ValueError("INVALID_MANIFEST")

    for name, content in blobs.items():
        if manifest.get("sha256", {}).get(name) != digest(content):
            raise ValueError("MANIFEST_HASH_MISMATCH")

    return validate(blobs)


def main() -> int:
    if len(sys.argv) != 1:
        print("SNAPSHOT_STATUS=BLOCKED_INVALID_ARGUMENTS")
        return 2

    if not DATA.is_dir() or DATA.is_symlink():
        print("SNAPSHOT_STATUS=BLOCKED_DATA_ROOT")
        return 1

    if GENERATIONS.is_symlink():
        print("SNAPSHOT_STATUS=BLOCKED_GENERATION_SYMLINK")
        return 1

    GENERATIONS.mkdir(mode=0o700, exist_ok=True)

    fd = os.open(
        LOCK,
        os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW,
        0o600,
    )

    generation = None
    activated = False

    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("SNAPSHOT_STATUS=ALREADY_RUNNING")
            return 1

        # Never replace a physical directory or arbitrary symlink.
        if CURRENT.is_symlink():
            previous = os.readlink(CURRENT)
            previous_name = Path(previous).name

            if (
                Path(previous).is_absolute()
                or Path(previous).parts != (
                    "generations", previous_name
                )
                or not NAME_PATTERN.fullmatch(previous_name)
            ):
                raise ValueError("UNTRUSTED_ACTIVE_POINTER")

            previous_dir = GENERATIONS / previous_name

            if not previous_dir.is_dir() or previous_dir.is_symlink():
                raise ValueError("ACTIVE_GENERATION_MISSING")

            verify_generation(previous_dir)

        elif CURRENT.exists():
            raise ValueError("ACTIVE_POINTER_NOT_SYMLINK")

        # Read and validate the existing legacy snapshot.
        blobs = {
            name: read_limited(DATA / name)
            for name in NAMES
        }
        stats = validate(blobs)

        # Unique, non-reused generation directory.
        stamp = datetime.now(timezone.utc).strftime(
            "%Y%m%dT%H%M%S"
        )
        name = (
            "generation_" + stamp + "_"
            + uuid.uuid4().hex[:12]
        )

        generation = GENERATIONS / name
        generation.mkdir(mode=0o700)

        for filename, content in blobs.items():
            target = generation / filename
            with target.open("xb") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            target.chmod(0o400)

        manifest = {
            "schema": "neurovest.snapshot.v1",
            "generation": name,
            "created_utc": datetime.now(
                timezone.utc
            ).isoformat(),
            "sha256": {
                filename: digest(content)
                for filename, content in blobs.items()
            },
            "statistics": stats,
            "limitations": [
                "Existing static dependency data",
                "No new source scan performed",
                "Legacy readers are not yet migrated",
            ],
        }

        manifest_path = generation / "manifest.json"
        with manifest_path.open("x", encoding="utf-8") as handle:
            json.dump(manifest, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())

        manifest_path.chmod(0o400)

        # Require source artifacts to remain identical
        # throughout publication.
        for filename, expected in blobs.items():
            if read_limited(DATA / filename) != expected:
                raise ValueError("LEGACY_SNAPSHOT_CHANGED")

        verify_generation(generation)
        generation.chmod(0o500)

        # Atomic pointer replacement on the same filesystem.
        pending = DATA / (
            ".current_" + uuid.uuid4().hex + ".pending"
        )

        try:
            os.symlink("generations/" + name, pending)
            os.replace(pending, CURRENT)
            activated = True
        finally:
            if pending.is_symlink():
                pending.unlink()

        # Validate through the new active pointer.
        verify_generation(CURRENT)

        print("SNAPSHOT_STATUS=PASS")
        print("ACTIVE_GENERATION=" + name)
        print("SOURCE_FILES=" + str(stats["source_files"]))
        print("FILE_DEPENDENCY_EDGES=" + str(stats["file_edges"]))
        print("BACKEND_STACKS=" + str(stats["backend_stacks"]))
        print(
            "CROSS_STACK_RELATIONSHIPS="
            + str(stats["cross_stack_relationships"])
        )
        print("MANIFEST_VERIFICATION=PASS")
        print("ATOMIC_POINTER_ACTIVATION=PASS")
        print("LEGACY_QUERY_READERS=UNCHANGED")
        print("APPLICATION_SOURCE_MODIFIED=False")
        print("BACKEND_RESTARTED=False")
        print("PATCH_APPLIED=False")
        return 0

    except (
        OSError, ValueError, TypeError,
        KeyError, json.JSONDecodeError
    ) as exc:
        print("SNAPSHOT_STATUS=FAILED")
        print("FAILURE_TYPE=" + type(exc).__name__)
        print("FAILURE_REASON=" + str(exc)[:120])

        # If activation did not happen, discard only the
        # new incomplete generation.
        if generation is not None and not activated:
            generation.chmod(0o700)
            shutil.rmtree(generation)

        return 1

    finally:
        os.close(fd)


if __name__ == "__main__":
    print("LEGACY_REPOSITORY_WRITER=RETIRED")
    print("USE_GENERATION_FIRST_WRITER=True")
    raise SystemExit(2)
