#!/usr/bin/env python3
"""Verified, generation-pinned NeuroVest repository snapshot reader."""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "runtime/qualification/repository_intelligence_v1"
GENERATIONS = DATA / "generations"
CURRENT = DATA / "current"

FILENAMES = (
    "inventory.json",
    "dependency_graph.json",
    "dependency_graph_v2.json",
)

MAX_BYTES = 20_000_000

GENERATION_NAME = re.compile(
    r"generation_[0-9]{8}T[0-9]{6}_[0-9a-f]{12}\Z"
)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def read_file(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError("UNSAFE_SNAPSHOT_ARTIFACT")

    if path.stat().st_size > MAX_BYTES:
        raise ValueError("SNAPSHOT_SIZE_LIMIT")

    raw = path.read_bytes()

    if len(raw) > MAX_BYTES:
        raise ValueError("SNAPSHOT_SIZE_LIMIT")

    return raw

def read_active_pair():
    """Return inventory and V2 graph from one verified generation.

    Resolve the active pointer exactly once. An activation occurring
    afterward cannot mix files from two different generations.
    """
    if (
        not CURRENT.is_symlink()
        or GENERATIONS.is_symlink()
        or DATA.is_symlink()
    ):
        raise ValueError("INVALID_ACTIVE_GENERATION")

    target = os.readlink(CURRENT)
    name = Path(target).name

    if (
        Path(target).is_absolute()
        or Path(target).parts != ("generations", name)
        or not GENERATION_NAME.fullmatch(name)
    ):
        raise ValueError("UNTRUSTED_ACTIVE_POINTER")

    directory = GENERATIONS / name

    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("GENERATION_NOT_AVAILABLE")

    blobs = {
        filename: read_file(directory / filename)
        for filename in FILENAMES
    }

    manifest = json.loads(
        read_file(directory / "manifest.json")
    )

    if (
        manifest.get("schema") != "neurovest.snapshot.v1"
        or manifest.get("generation") != name
    ):
        raise ValueError("INVALID_SNAPSHOT_MANIFEST")

    recorded = manifest.get("sha256")

    if not isinstance(recorded, dict):
        raise ValueError("INVALID_MANIFEST_HASHES")

    for filename, raw in blobs.items():
        if recorded.get(filename) != digest(raw):
            raise ValueError("SNAPSHOT_INTEGRITY_FAILURE")

    inventory = json.loads(blobs["inventory.json"])
    graph1 = json.loads(blobs["dependency_graph.json"])
    graph2 = json.loads(blobs["dependency_graph_v2.json"])

    if (
        inventory.get("schema")
        != "neurovest.repository_intelligence.v1"
        or graph1.get("schema")
        != "neurovest.repository_dependency_graph.v1"
        or graph2.get("schema")
        != "neurovest.repository_dependency_graph.v2"
    ):
        raise ValueError("SNAPSHOT_SCHEMA_MISMATCH")

    if (
        graph1.get("inventory_sha256")
        != digest(blobs["inventory.json"])
        or graph2.get("inventory_sha256")
        != digest(blobs["inventory.json"])
        or graph2.get("graph_v1_sha256")
        != digest(blobs["dependency_graph.json"])
    ):
        raise ValueError("SNAPSHOT_CHAIN_MISMATCH")

    return blobs["inventory.json"], blobs["dependency_graph_v2.json"]
