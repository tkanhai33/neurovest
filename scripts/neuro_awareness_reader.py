from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path

SCHEMA = "neuro_awareness_graph_v2r2_experimental"
MAX_GRAPH_BYTES = 10_000_000
MAX_PATH_LENGTH = 512
MAX_RESULTS = 20
MAX_HOPS = 10


class AwarenessError(Exception):
    pass


class AwarenessReader:
    def __init__(self, root: Path, graph_path: Path):
        self.root = root.resolve()
        self.graph_path = graph_path

        if not graph_path.is_file() or graph_path.is_symlink():
            raise AwarenessError("Graph unavailable")

        if graph_path.stat().st_size > MAX_GRAPH_BYTES:
            raise AwarenessError("Graph exceeds size limit")

        document = json.loads(
            graph_path.read_text(encoding="utf-8")
        )

        if document.get("schema") != SCHEMA:
            raise AwarenessError("Unsupported graph schema")

        raw_nodes = document.get("nodes")
        raw_edges = document.get("edges")

        if not isinstance(raw_nodes, list) or not isinstance(raw_edges, list):
            raise AwarenessError("Invalid graph structure")

        self.nodes = {}

        for node in raw_nodes:
            if not isinstance(node, dict):
                raise AwarenessError("Invalid node")

            identifier = node.get("id")
            fingerprint = node.get("sha256")

            self._validate_path(identifier)

            if (
                not isinstance(fingerprint, str)
                or len(fingerprint) != 64
                or any(c not in "0123456789abcdef" for c in fingerprint)
                or identifier in self.nodes
            ):
                raise AwarenessError("Invalid or duplicate node")

            self.nodes[identifier] = node

        self.edges = []
        self.incoming = defaultdict(list)
        self.outgoing = defaultdict(list)

        for edge in raw_edges:
            if not isinstance(edge, dict):
                raise AwarenessError("Invalid edge")

            source = edge.get("source")
            target = edge.get("target")

            if source not in self.nodes or target not in self.nodes:
                raise AwarenessError("Unresolved edge reference")

            if not isinstance(edge.get("kind"), str):
                raise AwarenessError("Missing edge classification")

            if not isinstance(edge.get("source_line"), int):
                raise AwarenessError("Missing source line")

            if edge["source_line"] < 1:
                raise AwarenessError("Invalid source line")

            self.edges.append(edge)
            self.incoming[target].append(edge)
            self.outgoing[source].append(edge)

        self.stale = self._check_fingerprints()

    @staticmethod
    def _validate_path(identifier):
        if not isinstance(identifier, str):
            raise AwarenessError("Invalid component path")

        if len(identifier) > MAX_PATH_LENGTH:
            raise AwarenessError("Component path too long")

        if "\\" in identifier or "\x00" in identifier:
            raise AwarenessError("Unsafe component path")

        path = Path(identifier)

        if (
            path.is_absolute()
            or ".." in path.parts
            or "." in path.parts
            or len(path.parts) < 2
            or path.parts[0] not in {"frontend", "backend"}
            or any(
                p.startswith(".next")
                or p in {"node_modules", ".git", ".venv", "runtime"}
                for p in path.parts
            )
        ):
            raise AwarenessError("Unsafe component path")

    def _check_fingerprints(self):
        stale = []

        for identifier, node in self.nodes.items():
            path = self.root / identifier

            if not path.is_file() or path.is_symlink():
                stale.append(identifier)
                continue

            try:
                if not path.resolve().is_relative_to(self.root):
                    stale.append(identifier)
                    continue

                actual = hashlib.sha256(
                    path.read_bytes()
                ).hexdigest()

                if actual != node["sha256"]:
                    stale.append(identifier)
            except OSError:
                stale.append(identifier)

        return stale

    def _require_fresh(self):
        if self.stale:
            raise AwarenessError(
                f"STALE_GRAPH: {len(self.stale)} source nodes changed; "
                "rebuild required"
            )

    def status(self):
        self._require_fresh()

        kinds = Counter(e["kind"] for e in self.edges)

        lines = [
            "NEURO_AWARENESS_STATUS",
            f"GRAPH_SCHEMA={SCHEMA}",
            f"SOURCE_NODES={len(self.nodes)}",
            f"CONNECTION_EDGES={len(self.edges)}",
            "SOURCE_FINGERPRINTS=PASS",
        ]

        for kind, count in sorted(kinds.items()):
            lines.append(f"EDGE_TYPE {kind}={count}")

        lines += [
            "GRAPH_MODE=STATIC_SOURCE_ANALYSIS",
            "RUNTIME_EXECUTION_VERIFIED=False",
            "DATABASE_CHAIN_COMPLETE=False",
            "SELF_MODIFICATION_ENABLED=False",
            "QUERY_STATUS=PASS",
        ]

        return "\n".join(lines)

    def inspect(self, identifier):
        self._validate_path(identifier)
        self._require_fresh()

        if identifier not in self.nodes:
            return "COMPONENT_NOT_INDEXED\nQUERY_STATUS=NOT_FOUND"

        incoming = self.incoming[identifier]
        outgoing = self.outgoing[identifier]

        lines = [
            "NEURO_AWARENESS_INSPECT",
            f"COMPONENT={identifier}",
            f"INCOMING_CONNECTIONS={len(incoming)}",
            f"OUTGOING_CONNECTIONS={len(outgoing)}",
            "",
            "DEPENDENTS:",
        ]

        for e in incoming[:MAX_RESULTS]:
            lines.append(
                f"{e['source']} | {e['kind']} | "
                f"{e.get('status', 'unknown')} | "
                f"line {e['source_line']}"
            )

        lines += [
            f"DEPENDENTS_TRUNCATED={len(incoming) > MAX_RESULTS}",
            "",
            "DEPENDENCIES:",
        ]

        for e in outgoing[:MAX_RESULTS]:
            lines.append(
                f"{e['target']} | {e['kind']} | "
                f"{e.get('status', 'unknown')} | "
                f"line {e['source_line']}"
            )

        lines += [
            f"DEPENDENCIES_TRUNCATED={len(outgoing) > MAX_RESULTS}",
            "RUNTIME_EXECUTION_VERIFIED=False",
            "QUERY_STATUS=PASS",
        ]

        return "\n".join(lines)

    def trace(self, start, finish):
        self._validate_path(start)
        self._validate_path(finish)
        self._require_fresh()

        if start not in self.nodes or finish not in self.nodes:
            return "TRACE_NODE_NOT_INDEXED\nQUERY_STATUS=NOT_FOUND"

        queue = deque([(start, [])])
        visited = {start}

        while queue:
            current, chain = queue.popleft()

            if current == finish:
                lines = [
                    "NEURO_AWARENESS_TRACE",
                    f"FROM={start}",
                    f"TO={finish}",
                    "PATH_STATUS=STATIC_GRAPH_PATH_FOUND",
                    f"HOPS={len(chain)}",
                ]

                for edge in chain:
                    lines.append(
                        f"{edge['source']} -> {edge['target']} "
                        f"| {edge['kind']} "
                        f"| {edge.get('status', 'unknown')} "
                        f"| line {edge['source_line']}"
                    )

                lines += [
                    "RUNTIME_EXECUTION_VERIFIED=False",
                    "QUERY_STATUS=PASS",
                ]

                return "\n".join(lines)

            if len(chain) >= MAX_HOPS:
                continue

            for edge in self.outgoing[current]:
                target = edge["target"]

                if target not in visited:
                    visited.add(target)
                    queue.append((target, chain + [edge]))

        return (
            "PATH_STATUS=NOT_FOUND_IN_STATIC_GRAPH\n"
            "QUERY_STATUS=NOT_FOUND"
        )


def main():
    if len(sys.argv) < 4:
        raise AwarenessError(
            "Usage: awareness_reader.py ROOT GRAPH status|inspect|trace"
        )

    root = Path(sys.argv[1])
    graph = Path(sys.argv[2])
    command = sys.argv[3]

    reader = AwarenessReader(root, graph)

    if command == "status" and len(sys.argv) == 4:
        print(reader.status())

    elif command == "inspect" and len(sys.argv) == 5:
        print(reader.inspect(sys.argv[4]))

    elif command == "trace" and len(sys.argv) == 6:
        print(reader.trace(sys.argv[4], sys.argv[5]))

    else:
        raise AwarenessError("Invalid awareness query")


if __name__ == "__main__":
    try:
        main()
    except (AwarenessError, OSError, ValueError) as error:
        print(
            f"AWARENESS_ERROR={error}\nQUERY_STATUS=FAIL",
            file=sys.stderr,
        )
        raise SystemExit(1)
