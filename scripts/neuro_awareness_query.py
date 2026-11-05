from __future__ import annotations

import sys
from pathlib import Path

from neuro_awareness_reader import AwarenessReader, AwarenessError

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "neuro_awareness_graph_v2r2_experimental"

def main(root: Path, graph: Path, args: list[str]) -> str:
    if not args:
        raise AwarenessError("Missing command")

    reader = AwarenessReader(root, graph)

    if args == ["status"]:
        return reader.status()

    if len(args) == 2 and args[0] == "inspect":
        return reader.inspect(args[1])

    if len(args) == 3 and args[0] == "trace":
        return reader.trace(args[1], args[2])

    raise AwarenessError("Invalid awareness command")

if __name__ == "__main__":
    # Installed layout: ROOT/scripts/neuro_awareness_query.py
    root = Path(__file__).resolve().parents[1]

    candidates = sorted(
        (root / "runtime/qualification").glob(
            "neuro_awareness_v2r2_*/awareness_graph_v2r2.json"
        ),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not candidates:
        print("QUERY_STATUS=FAIL")
        raise SystemExit(1)

    try:
        print(main(root, candidates[0], sys.argv[1:]))
    except (AwarenessError, OSError, ValueError) as exc:
        print("AWARENESS_QUERY_UNAVAILABLE")
        print("QUERY_STATUS=FAIL")
        raise SystemExit(1)
