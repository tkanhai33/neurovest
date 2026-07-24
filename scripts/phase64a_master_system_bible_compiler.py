#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json
import hashlib

ROOT = Path(".").resolve()
HANDOFF = ROOT / "handoff"
PROJECT_BIBLE = HANDOFF / "project_bible"
ATLAS = PROJECT_BIBLE / "architecture_atlas"
OUT = HANDOFF / "MASTER_SYSTEM_BIBLE"

PHASE = "64A_MASTER_SYSTEM_BIBLE_COMPILER"

OUT.mkdir(parents=True, exist_ok=True)

TEXT_EXTENSIONS = {".md", ".txt", ".mmd"}
JSON_EXTENSIONS = {".json"}

IGNORE_NAMES = {
    "MASTER_SYSTEM_BIBLE.md",
    "MASTER_SYSTEM_BIBLE.json",
}


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def title_from_path(path: Path) -> str:
    name = path.stem.replace("_", " ").replace("-", " ").strip()
    return " ".join(word.capitalize() for word in name.split())


def file_hash(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except Exception:
        return ""


def fenced(path: Path, text: str) -> str:
    suffix = path.suffix.lower()

    if suffix == ".json":
        return f"```json\n{text.strip()}\n```"

    if suffix in {".txt", ".mmd"}:
        return f"```text\n{text.rstrip()}\n```"

    return text.rstrip()


def collect_sources() -> list[Path]:
    priority = [
        PROJECT_BIBLE / "PROJECT_BIBLE.md",
        ATLAS / "ARCHITECTURE_ATLAS.md",
        PROJECT_BIBLE / "EXECUTIVE_SUMMARY.md",
        HANDOFF / "repository_tree.txt",
        HANDOFF / "backend_tree.txt",
        HANDOFF / "frontend_tree.txt",
        HANDOFF / "runtime_tree.txt",
        HANDOFF / "audit_tree.txt",
        HANDOFF / "canonical_layer_map.txt",
        HANDOFF / "stack_topology.txt",
        ATLAS / "STACK_OWNERSHIP.md",
        ATLAS / "LAYER_OWNERSHIP.md",
        HANDOFF / "runtime_node_graph.txt",
        ATLAS / "TOPOLOGY" / "node_graph.md",
        HANDOFF / "dependency_graph.txt",
        ATLAS / "TOPOLOGY" / "dependency_graph.md",
        HANDOFF / "runtime_state_machine.txt",
        PROJECT_BIBLE / "DATA_FLOW.md",
        ATLAS / "FLOWS" / "market_data.md",
        ATLAS / "FLOWS" / "candidate_pipeline.md",
        ATLAS / "FLOWS" / "execution_disabled.md",
        PROJECT_BIBLE / "QWEN_READ_ONLY_ARCHITECTURE.md",
        HANDOFF / "certification_timeline.txt",
        ATLAS / "PHASE_TIMELINE.md",
        PROJECT_BIBLE / "DEVELOPER_RULEBOOK.md",
        PROJECT_BIBLE / "ROADMAP.md",
        PROJECT_BIBLE / "GLOSSARY.md",
        PROJECT_BIBLE / "TRACEABILITY_INDEX.md",
        HANDOFF / "repository_statistics.json",
        HANDOFF / "certified_phase_index.json",
        HANDOFF / "topology_summary.json",
        PROJECT_BIBLE / "PROJECT_BIBLE.json",
        ATLAS / "ARCHITECTURE_ATLAS.json",
        ATLAS / "IMPORT_DEPENDENCY_ATLAS.json",
    ]

    seen = set()
    sources = []

    for path in priority:
        if path.exists() and path.name not in IGNORE_NAMES:
            sources.append(path)
            seen.add(path.resolve())

    for root in [HANDOFF, PROJECT_BIBLE, ATLAS]:
        if not root.exists():
            continue

        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            if path.name in IGNORE_NAMES:
                continue
            if path.suffix.lower() not in TEXT_EXTENSIONS | JSON_EXTENSIONS:
                continue
            if path.resolve() in seen:
                continue

            sources.append(path)
            seen.add(path.resolve())

    return sources


def chapter_category(path: Path) -> str:
    p = str(path)

    if "EXECUTIVE_SUMMARY" in p:
        return "Executive"
    if "TREE" in p.upper() or "tree" in path.name.lower():
        return "Repository Topology"
    if "LAYER" in p.upper():
        return "Layer Architecture"
    if "STACK" in p.upper():
        return "Stack Architecture"
    if "NODE" in p.upper() or "TOPOLOGY" in p.upper():
        return "Node / Topology"
    if "DEPENDENCY" in p.upper() or "IMPORT" in p.upper():
        return "Dependency Atlas"
    if "STATE_MACHINE" in p.upper():
        return "Runtime State"
    if "FLOW" in p.upper():
        return "Flows"
    if "QWEN" in p.upper():
        return "Qwen Read-Only"
    if "TIMELINE" in p.upper() or "CERTIFICATION" in p.upper() or "certified_phase" in p:
        return "Certification History"
    if "RULEBOOK" in p.upper():
        return "Governance"
    if "ROADMAP" in p.upper():
        return "Roadmap"
    if "GLOSSARY" in p.upper():
        return "Glossary"
    if "TRACEABILITY" in p.upper():
        return "Traceability"
    if path.suffix.lower() == ".json":
        return "Machine Index"
    return "Reference"


def main() -> None:
    sources = collect_sources()

    manifest = []
    grouped = {}

    for path in sources:
        text = read(path)
        if not text.strip():
            continue

        category = chapter_category(path)
        grouped.setdefault(category, []).append(path)

        manifest.append({
            "path": str(path.relative_to(ROOT)),
            "category": category,
            "bytes": path.stat().st_size,
            "sha256": file_hash(path),
        })

    doc = []
    doc.append("# NEUROVEST MASTER SYSTEM BIBLE")
    doc.append("")
    doc.append(f"Generated: {datetime.now(UTC).isoformat()}")
    doc.append(f"Compiler: {PHASE}")
    doc.append("Mode: READ ONLY DOCUMENTATION COMPILER")
    doc.append("")
    doc.append("> This file is compiled from existing generated handoff, Project Bible, Architecture Atlas, topology, timeline, and traceability artifacts.")
    doc.append("")
    doc.append("---")
    doc.append("")
    doc.append("# Table of Contents")
    doc.append("")

    chapter_no = 1
    ordered_categories = [
        "Executive",
        "Reference",
        "Repository Topology",
        "Layer Architecture",
        "Stack Architecture",
        "Node / Topology",
        "Dependency Atlas",
        "Runtime State",
        "Flows",
        "Qwen Read-Only",
        "Certification History",
        "Governance",
        "Roadmap",
        "Glossary",
        "Traceability",
        "Machine Index",
    ]

    toc_entries = []

    for category in ordered_categories:
        for path in grouped.get(category, []):
            title = title_from_path(path)
            toc_entries.append((chapter_no, category, title, path))
            doc.append(f"{chapter_no}. [{category}] {title}")
            chapter_no += 1

    doc.append("")
    doc.append("---")
    doc.append("")

    for number, category, title, path in toc_entries:
        text = read(path)

        doc.append(f"# {number}. [{category}] {title}")
        doc.append("")
        doc.append(f"Source: `{path.relative_to(ROOT)}`")
        doc.append("")
        doc.append(fenced(path, text))
        doc.append("")
        doc.append("---")
        doc.append("")

    doc.append("# Appendix A — Source Manifest")
    doc.append("")
    doc.append("```json")
    doc.append(json.dumps(manifest, indent=2))
    doc.append("```")
    doc.append("")

    master = "\n".join(doc)

    write(OUT / "MASTER_SYSTEM_BIBLE.md", master)

    index = {
        "phase": PHASE,
        "generated_at": datetime.now(UTC).isoformat(),
        "mode": "READ_ONLY_DOCUMENTATION_COMPILER",
        "source_count": len(manifest),
        "categories": {
            category: len(grouped.get(category, []))
            for category in ordered_categories
        },
        "output_markdown": str((OUT / "MASTER_SYSTEM_BIBLE.md").relative_to(ROOT)),
        "source_manifest": manifest,
        "certified": True,
    }

    write(OUT / "MASTER_SYSTEM_BIBLE.json", json.dumps(index, indent=2))

    print(json.dumps(index, indent=2))
    print()
    print("MASTER SYSTEM BIBLE GENERATED")
    print(OUT / "MASTER_SYSTEM_BIBLE.md")


if __name__ == "__main__":
    main()
