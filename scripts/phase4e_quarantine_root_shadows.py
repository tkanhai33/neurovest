#!/usr/bin/env python3
import json
import shutil
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
QUARANTINE = ROOT / "quarantine_artifacts" / "phase4e_root_stack_shadows"
OUT_DIR = ROOT / "runtime" / "repo_memory"
OUT_DIR.mkdir(parents=True, exist_ok=True)
QUARANTINE.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "phase4e_quarantine_root_shadows_latest.json"

TARGETS = [
    "ledger.py",
    "paper_broker.py",
]

KEEP_ROOT = [
    "generate_wire_graph.py",
    "neuro_cli.py",
    "neuro_engineer.py",
]


def move_file(rel: str):
    src = ROOT / rel
    dst = QUARANTINE / rel

    if not src.exists():
        return {
            "source": rel,
            "moved": False,
            "reason": "source_missing",
            "target": str(dst.relative_to(ROOT)),
        }

    if dst.exists():
        return {
            "source": rel,
            "moved": False,
            "reason": "target_already_exists",
            "target": str(dst.relative_to(ROOT)),
        }

    shutil.move(str(src), str(dst))

    return {
        "source": rel,
        "moved": True,
        "reason": "quarantined_root_shadow",
        "target": str(dst.relative_to(ROOT)),
    }


def main():
    moves = [move_file(rel) for rel in TARGETS]

    report = {
        "phase": "4E_QUARANTINE_ROOT_STACK_SHADOWS",
        "generated_at": datetime.now(UTC).isoformat(),
        "targets": TARGETS,
        "kept_root": KEEP_ROOT,
        "moves": moves,
    }

    OUT_JSON.write_text(json.dumps(report, indent=2))

    print(json.dumps({
        "phase": report["phase"],
        "moves": moves,
        "kept_root": KEEP_ROOT,
        "output": str(OUT_JSON),
    }, indent=2))


if __name__ == "__main__":
    main()
