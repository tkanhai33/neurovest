#!/usr/bin/env python3
"""NeuroVest generation-first repository refresh.

Build -> validate -> immutable generation -> atomic activation.
No application patches or legacy snapshot writes.
"""
from __future__ import annotations

import fcntl
import hashlib
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
DATA = ROOT / "runtime/qualification/repository_intelligence_v1"
GENERATIONS = DATA / "generations"
CURRENT = DATA / "current"
LOCK = DATA / "generation_first_writer.lock"

NAMES = (
    "inventory.json",
    "dependency_graph.json",
    "dependency_graph_v2.json",
)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def require(condition, reason):
    if not condition:
        raise ValueError(reason)

def module(name, filename):
    path = SCRIPTS / filename
    require(path.is_file() and not path.is_symlink(),
            "MISSING_OR_UNSAFE_" + filename)
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None,
            "IMPORT_FAILED_" + name)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded

def write_immutable(directory, name, raw):
    target = directory / name
    with target.open("xb") as file:
        file.write(raw)
        file.flush()
        os.fsync(file.fileno())
    target.chmod(0o400)

def run(dry_run):
    scanner = module(
        "nv_generation_scanner", "neuro_repository_intelligence.py"
    )
    builder = module(
        "nv_generation_builder", "neuro_repository_refresh.py"
    )
    validator = module(
        "nv_generation_validator", "neuro_repository_snapshot.py"
    )

    require(hasattr(scanner, "OUT") and hasattr(scanner, "main"),
            "SCANNER_INTERFACE_CHANGED")
    require(hasattr(builder, "INDEX")
            and hasattr(builder, "build_graphs"),
            "BUILDER_INTERFACE_CHANGED")
    require(hasattr(validator, "validate")
            and hasattr(validator, "verify_generation"),
            "VALIDATOR_INTERFACE_CHANGED")

    require(DATA.is_dir() and not DATA.is_symlink(),
            "UNSAFE_DATA_DIRECTORY")
    require(GENERATIONS.is_dir() and not GENERATIONS.is_symlink(),
            "UNSAFE_GENERATION_DIRECTORY")
    require(CURRENT.is_symlink(), "ACTIVE_GENERATION_MISSING")

    # Verify the previous active generation before starting.
    old_pointer = os.readlink(CURRENT)
    require(
        old_pointer.startswith("generations/generation_")
        and len(Path(old_pointer).parts) == 2,
        "UNTRUSTED_ACTIVE_POINTER",
    )
    previous = DATA / old_pointer
    validator.verify_generation(previous)

    legacy_hashes = {
        name: digest((DATA / name).read_bytes())
        for name in NAMES
    }

    with tempfile.TemporaryDirectory(
        prefix="neuro_generation_build_",
        dir=ROOT / "runtime/qualification",
    ) as temporary:
        stage = Path(temporary)
        stage.chmod(0o700)

        scanner.OUT = stage
        builder.INDEX = stage / "inventory.json"

        print("SOURCE_SCAN=STARTED", flush=True)
        result = scanner.main()
        require(result is None or result == 0,
                "SOURCE_SCANNER_FAILED")

        index_path = stage / "inventory.json"
        require(index_path.is_file(), "STAGED_INVENTORY_MISSING")

        graph1, graph2 = builder.build_graphs()

        raw1 = (
            json.dumps(graph1, indent=2) + "\n"
        ).encode("utf-8")
        graph2["graph_v1_sha256"] = digest(raw1)
        raw2 = (
            json.dumps(graph2, indent=2) + "\n"
        ).encode("utf-8")

        blobs = {
            "inventory.json": index_path.read_bytes(),
            "dependency_graph.json": raw1,
            "dependency_graph_v2.json": raw2,
        }

        require(all(len(raw) <= 20_000_000 for raw in blobs.values()),
                "SNAPSHOT_SIZE_LIMIT")

        stats = validator.validate(blobs)

        # NEUROVEST_ATOMIC_FIVE_ARTIFACT_PUBLISHER_V1
        indexer = module(
            "nv_atomic_function_index",
            "neuro_repository_function_index.py",
        )
        grapher = module(
            "nv_atomic_function_graph",
            "neuro_repository_function_graph.py",
        )
        five_reader = module(
            "nv_atomic_five_reader",
            "neuro_repository_five_artifact_reader.py",
        )

        def staged_pair():
            return (
                blobs["inventory.json"],
                blobs["dependency_graph_v2.json"],
            )

        indexer.read_active_pair = staged_pair
        indexer.DATA = stage
        indexer.OUTPUT = stage / "function_intelligence_v1.json"

        grapher.read_active_pair = staged_pair
        grapher.DATA = stage
        grapher.FUNCTION_INDEX = indexer.OUTPUT
        grapher.OUTPUT = stage / "function_call_graph_v1.json"

        original_argv = sys.argv
        try:
            sys.argv = [original_argv[0]]
            require(indexer.main() is None,
                    "FUNCTION_INDEX_BUILD_FAILED")
            require(grapher.main() is None,
                    "FUNCTION_GRAPH_BUILD_FAILED")
        finally:
            sys.argv = original_argv

        function_raw = indexer.OUTPUT.read_bytes()
        call_raw = grapher.OUTPUT.read_bytes()

        function_doc = json.loads(function_raw)
        call_doc = json.loads(call_raw)

        require(
            function_doc.get("schema")
            == "neurovest.function_intelligence.v1"
            and call_doc.get("schema")
            == "neurovest.function_call_graph.v1",
            "FUNCTION_ARTIFACT_SCHEMA",
        )

        require(
            function_doc.get("inventory_sha256")
            == digest(blobs["inventory.json"])
            and function_doc.get("graph_v2_sha256")
            == digest(blobs["dependency_graph_v2.json"])
            and call_doc.get("function_index_sha256")
            == digest(function_raw)
            and call_doc.get("inventory_sha256")
            == digest(blobs["inventory.json"])
            and call_doc.get("graph_v2_sha256")
            == digest(blobs["dependency_graph_v2.json"]),
            "FUNCTION_HASH_CHAIN_FAILED",
        )

        functions = function_doc.get("functions")
        edges = call_doc.get("edges")
        status = function_doc.get("status")

        require(
            isinstance(functions, list)
            and len(functions) <= 50000
            and isinstance(edges, list)
            and len(edges) <= 100000
            and function_doc.get("function_count") == len(functions)
            and call_doc.get("indexed_functions") == len(functions)
            and call_doc.get("candidate_edges") == len(edges),
            "FUNCTION_STRUCTURE_FAILED",
        )

        require(isinstance(status, dict), "INDEX_STATUS_MISSING")

        for key in (
            "changed_since_snapshot",
            "unsafe_or_missing",
            "invalid_fingerprint",
            "size_limit",
            "read_error",
        ):
            require(
                status.get(key, 0) == 0,
                "FUNCTION_INDEX_INCOMPLETE_" + key,
            )

        blobs["function_intelligence_v1.json"] = function_raw
        blobs["function_call_graph_v1.json"] = call_raw

        require(
            len(blobs) == 5
            and all(len(raw) <= 20_000_000
                    for raw in blobs.values()),
            "FIVE_ARTIFACT_LIMIT_FAILED",
        )

        validator.validate(blobs)

        print("FIVE_ARTIFACT_STAGING=PASS")
        print("INDEXED_FUNCTIONS=", len(functions))
        print("CANDIDATE_CALL_EDGES=", len(edges))
        print("FUNCTION_HASH_CHAIN=PASS")


        print("STAGED_GRAPH_VALIDATION=PASS")
        print("SOURCE_FILES=", stats["source_files"])
        print("FILE_DEPENDENCY_EDGES=", stats["file_edges"])
        print("BACKEND_STACKS=", stats["backend_stacks"])
        print(
            "CROSS_STACK_RELATIONSHIPS=",
            stats["cross_stack_relationships"],
        )

        if dry_run:
            require(os.readlink(CURRENT) == old_pointer,
                    "ACTIVE_POINTER_CHANGED_DURING_DRY_RUN")
            require(
                all(
                    digest((DATA / name).read_bytes()) == legacy_hashes[name]
                    for name in NAMES
                ),
                "LEGACY_SNAPSHOT_CHANGED_DURING_DRY_RUN",
            )
            print("DRY_RUN=PASS")
            print("ACTIVE_POINTER_UNCHANGED=True")
            print("LEGACY_SNAPSHOTS_UNCHANGED=True")
            print("GENERATION_FIRST_WRITER=PASS")
            return

        # Publication begins only after complete staged validation.
        require(os.readlink(CURRENT) == old_pointer,
                "ACTIVE_POINTER_CHANGED_DURING_BUILD")

        generation_name = (
            datetime.now(timezone.utc).strftime(
                "generation_%Y%m%dT%H%M%S_"
            )
            + uuid.uuid4().hex[:12]
        )
        generation = GENERATIONS / generation_name
        activated = False

        try:
            generation.mkdir(mode=0o700)

            for name, raw in blobs.items():
                write_immutable(generation, name, raw)

            manifest = {
                "schema": "neurovest.snapshot.v1",
                "generation": generation_name,
                "created_utc": datetime.now(
                    timezone.utc
                ).isoformat(),
                "sha256": {
                    name: digest(raw)
                    for name, raw in blobs.items()
                },
                "statistics": stats,
                "limitations": [
                    "Static imports and candidate calls only",
                    "Dynamic and runtime dependencies incomplete",
                    "Source scan may report existing syntax errors",
                    "No application source modifications",
                ],
            }

            manifest_raw = (
                json.dumps(manifest, indent=2) + "\n"
            ).encode("utf-8")
            write_immutable(
                generation, "manifest.json", manifest_raw
            )

            validator.verify_generation(generation)
            generation.chmod(0o500)

            pending = DATA / (
                ".current_" + uuid.uuid4().hex + ".pending"
            )

            try:
                require(
                    os.readlink(CURRENT) == old_pointer,
                    "ACTIVE_POINTER_CHANGED_BEFORE_COMMIT",
                )
                os.symlink(
                    "generations/" + generation_name, pending
                )

                # Verify the complete generation through the pending
                # pointer BEFORE changing the live active pointer.
                five_reader.CURRENT = pending
                checked_name, checked_blobs = five_reader.read_bundle()
                require(
                    checked_name == generation_name
                    and len(checked_blobs) == 5,
                    "FIVE_ARTIFACT_PREACTIVATION_FAILED",
                )
                print("FIVE_ARTIFACT_PREACTIVATION=PASS")

                os.replace(pending, CURRENT)
                activated = True
            finally:
                if pending.is_symlink():
                    pending.unlink()

            validator.verify_generation(generation)

            require(
                os.readlink(CURRENT)
                == "generations/" + generation_name,
                "ACTIVATION_POINTER_MISMATCH",
            )

            print("IMMUTABLE_SNAPSHOT=VERIFIED")
            print("ATOMIC_ACTIVATION=PASS")
            print("ACTIVE_GENERATION=", generation_name)
            print("GENERATION_FIRST_WRITER=PASS")
            print("REPOSITORY_REFRESH=PASS")

        finally:
            if not activated and generation.exists():
                generation.chmod(0o700)
                for child in generation.iterdir():
                    child.chmod(0o600)
                shutil.rmtree(generation)

        # The legacy files are retained, not updated.
        require(
            all(
                digest((DATA / name).read_bytes())
                == legacy_hashes[name]
                for name in NAMES
            ),
            "LEGACY_FILES_CHANGED",
        )
        print("LEGACY_SNAPSHOT_WRITES=False")

def main():
    if sys.argv[1:] == ["--dry-run"]:
        dry_run = True
    elif len(sys.argv) == 1:
        dry_run = False
    else:
        print("GENERATION_FIRST_WRITER=BLOCKED")
        return 2

    fd = None
    try:
        fd = os.open(
            LOCK, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600
        )
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

        run(dry_run)
        print("APPLICATION_SOURCE_MODIFIED=False")
        print("DATABASE_MODIFIED=False")
        print("BACKEND_RESTARTED=False")
        print("PATCH_APPLIED=False")
        return 0

    except BlockingIOError:
        print("GENERATION_FIRST_WRITER=ALREADY_RUNNING")
        return 1
    except Exception as exc:
        print("GENERATION_FIRST_WRITER=FAILED")
        print("FAILURE_TYPE=", type(exc).__name__)
        print("FAILURE_REASON=", str(exc)[:180])
        return 1
    finally:
        if fd is not None:
            os.close(fd)

if __name__ == "__main__":
    raise SystemExit(main())
