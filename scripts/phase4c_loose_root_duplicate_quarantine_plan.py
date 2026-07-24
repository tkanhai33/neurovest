#!/usr/bin/env python3
import json
import hashlib
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT_DIR = ROOT / "runtime" / "repo_memory"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "phase4c_loose_root_duplicate_quarantine_plan_latest.json"

CANDIDATES = [
    "ledger.py",
    "paper_broker.py",
    "generate_wire_graph.py",
    "neuro_cli.py",
    "neuro_engineer.py",
]

CANONICAL_MAP = {
    "ledger.py": "backend/app/stacks/journal_ledger/ledger.py",
    "paper_broker.py": "backend/app/stacks/execution/paper_broker.py",
    "generate_wire_graph.py": None,
    "neuro_cli.py": None,
    "neuro_engineer.py": None,
}


def sha256(path: Path):
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_info(path: Path):
    return {
        "path": str(path.relative_to(ROOT)),
        "exists": path.exists(),
        "sha256": sha256(path),
        "size_bytes": path.stat().st_size if path.exists() else None,
    }


def main():
    moves = []

    for rel in CANDIDATES:
        source = ROOT / rel
        canonical_rel = CANONICAL_MAP.get(rel)
        canonical = ROOT / canonical_rel if canonical_rel else None

        source_info = file_info(source)
        canonical_info = file_info(canonical) if canonical else None

        duplicate_of_canonical = (
            source_info["exists"]
            and canonical_info
            and canonical_info["exists"]
            and source_info["sha256"] == canonical_info["sha256"]
        )

        if rel in {"ledger.py", "paper_broker.py"}:
            risk = "HIGH_DUPLICATE_STACK_SHADOW"
            recommendation = "quarantine_after_manual_confirm"
        elif rel == "generate_wire_graph.py":
            risk = "KEEP_ROOT_TOOLING"
            recommendation = "keep_root"
        elif rel == "neuro_cli.py":
            risk = "KEEP_ROOT_CLI"
            recommendation = "keep_root"
        else:
            risk = "REVIEW_ROOT_TOOLING"
            recommendation = "manual_review"

        moves.append({
            "source": source_info,
            "canonical": canonical_info,
            "duplicate_of_canonical": duplicate_of_canonical,
            "risk": risk,
            "recommendation": recommendation,
            "dry_run_target": (
                f"quarantine_artifacts/phase4c_loose_root_duplicates/{rel}"
                if recommendation.startswith("quarantine")
                else None
            ),
        })

    report = {
        "phase": "4C_LOOSE_ROOT_DUPLICATE_QUARANTINE_PLAN",
        "generated_at": datetime.now(UTC).isoformat(),
        "dry_run_only": True,
        "safe_to_move_now": False,
        "moves": moves,
    }

    OUT_JSON.write_text(json.dumps(report, indent=2))

    print(json.dumps({
        "phase": report["phase"],
        "dry_run_only": True,
        "safe_to_move_now": False,
        "output": str(OUT_JSON),
        "move_candidates": [
            {
                "source": m["source"]["path"],
                "risk": m["risk"],
                "recommendation": m["recommendation"],
                "duplicate_of_canonical": m["duplicate_of_canonical"],
                "target": m["dry_run_target"],
            }
            for m in moves
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
