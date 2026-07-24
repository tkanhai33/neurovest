from __future__ import annotations

from typing import Any, Callable

from backend.app.stacks.chat_public.capability_state_registry import (
    build_capability_registry,
    capability_summary_lines,
)

from backend.app.stacks.chat_public.context_loader import (
    architecture_dashboard,
    load_component_overlay_v1,
    load_dependency_graph_v1,
    load_repo_context,
    repo_component_hotspots,
    repo_hotspots,
)


def _safe_load(
    loader: Callable[[], Any],
    fallback: Any,
) -> tuple[Any, str | None]:
    try:
        return loader(), None
    except Exception as exc:
        return (
            fallback,
            f"{type(exc).__name__}: {exc}",
        )


def _integer(
    value: Any,
    default: int = 0,
) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _hotspot_names(
    payload: Any,
    *,
    limit: int = 5,
) -> list[str]:
    if not isinstance(payload, dict):
        return []

    rows = payload.get("hotspots", [])

    if not isinstance(rows, list):
        return []

    names: list[str] = []

    for row in rows:
        if not isinstance(row, dict):
            continue

        name = (
            row.get("component")
            or row.get("module")
            or row.get("file")
            or row.get("name")
            or row.get("node")
        )

        if not name:
            continue

        degree = (
            row.get("total_degree")
            or row.get("degree")
            or row.get("out_degree")
            or row.get("in_degree")
        )

        if degree is None:
            names.append(str(name))
        else:
            names.append(
                f"{name} (degree={degree})"
            )

        if len(names) >= limit:
            break

    return names


def _bullet_lines(
    values: list[str],
) -> str:
    if not values:
        return "- No qualifying items were present in the loaded evidence."

    return "\n".join(
        f"- {value}"
        for value in values
    )


def build_developer_response(
    *,
    subtype: str,
) -> str:
    """
    Build a deterministic developer response using existing local evidence.

    No model inference, repository mutation, test execution, external API
    request, broker action, or live-trading operation occurs here.
    """

    repo, repo_error = _safe_load(
        lambda: load_repo_context(limit=10),
        {
            "file_count": 0,
            "sample_files": [],
        },
    )

    dependency_graph, graph_error = _safe_load(
        load_dependency_graph_v1,
        {
            "nodes": [],
            "edges": [],
            "top_imported": [],
            "top_importers": [],
        },
    )

    dependency_hotspots, dependency_hotspot_error = _safe_load(
        lambda: repo_hotspots(limit=8),
        {
            "hotspot_count": 0,
            "hotspots": [],
        },
    )

    component_overlay, component_error = _safe_load(
        load_component_overlay_v1,
        {
            "components": {},
            "component_edges": {},
        },
    )

    component_hotspots, component_hotspot_error = _safe_load(
        lambda: repo_component_hotspots(limit=8),
        {
            "hotspot_count": 0,
            "hotspots": [],
        },
    )

    architecture, architecture_error = _safe_load(
        architecture_dashboard,
        {
            "found": False,
            "status": None,
            "drift_count": None,
            "summary_text": "",
            "dashboard": {},
        },
    )


    capability_registry, capability_error = _safe_load(
        build_capability_registry,
        {
            "registry_version": "stage3.v1",
            "read_only": True,
            "source_count": 0,
            "verified_count": 0,
            "available_count": 0,
            "operational_count": 0,
            "attention_count": 0,
            "states": [],
        },
    )

    repo = repo if isinstance(repo, dict) else {}
    dependency_graph = (
        dependency_graph
        if isinstance(dependency_graph, dict)
        else {}
    )
    component_overlay = (
        component_overlay
        if isinstance(component_overlay, dict)
        else {}
    )
    architecture = (
        architecture
        if isinstance(architecture, dict)
        else {}
    )


    capability_registry = (
        capability_registry
        if isinstance(capability_registry, dict)
        else {}
    )

    file_count = _integer(
        repo.get("file_count")
    )

    node_count = len(
        dependency_graph.get("nodes", [])
    ) if isinstance(
        dependency_graph.get("nodes", []),
        list,
    ) else 0

    edge_count = len(
        dependency_graph.get("edges", [])
    ) if isinstance(
        dependency_graph.get("edges", []),
        list,
    ) else 0

    components = component_overlay.get(
        "components",
        {},
    )

    component_count = (
        len(components)
        if isinstance(components, dict)
        else 0
    )

    architecture_found = bool(
        architecture.get("found")
    )

    architecture_status = architecture.get(
        "status"
    )

    drift_count = architecture.get(
        "drift_count"
    )

    capability_lines = capability_summary_lines(
        capability_registry
    )

    verified_capability_count = _integer(
        capability_registry.get(
            "verified_count"
        )
    )

    operational_capability_count = _integer(
        capability_registry.get(
            "operational_count"
        )
    )

    capability_source_count = _integer(
        capability_registry.get(
            "source_count"
        )
    )

    capability_attention_count = _integer(
        capability_registry.get(
            "attention_count"
        )
    )

    proven: list[str] = []

    if file_count:
        proven.append(
            f"The repository index currently reports {file_count} files."
        )
    else:
        proven.append(
            "The repository index loaded, but it did not provide a positive "
            "file count."
        )

    if node_count or edge_count:
        proven.append(
            "The dependency graph currently contains "
            f"{node_count} nodes and {edge_count} edges."
        )
    else:
        proven.append(
            "The dependency graph loader did not provide populated nodes "
            "and edges."
        )

    if component_count:
        proven.append(
            f"The component overlay currently identifies {component_count} "
            "components."
        )
    else:
        proven.append(
            "The component overlay did not provide a populated component map."
        )

    if architecture_found:
        proven.append(
            "The architecture dashboard is available with "
            f"status={architecture_status!r} and "
            f"drift_count={drift_count!r}."
        )
    else:
        proven.append(
            "The architecture dashboard was not available from the current "
            "runtime evidence."
        )


    proven.append(
        "The read-only capability registry inspected "
        f"{capability_source_count} sources; "
        f"{verified_capability_count} were synchronously verified and "
        f"{operational_capability_count} reported as operational."
    )

    hotspot_rows = (
        _hotspot_names(
            dependency_hotspots,
            limit=5,
        )
        + _hotspot_names(
            component_hotspots,
            limit=5,
        )
    )

    limitations: list[str] = []

    if hotspot_rows:
        limitations.append(
            "The repository contains high-connectivity areas that require "
            "focused inspection before changing their boundaries: "
            + ", ".join(hotspot_rows[:6])
            + "."
        )

    if not architecture_found:
        limitations.append(
            "Architecture-health conclusions are limited because the "
            "dashboard evidence is unavailable."
        )

    loader_errors = [
        error
        for error in (
            repo_error,
            graph_error,
            dependency_hotspot_error,
            component_error,
            component_hotspot_error,
            architecture_error,
            capability_error,
        )
        if error
    ]

    if loader_errors:
        limitations.append(
            "One or more local evidence loaders failed, so this assessment "
            "is incomplete."
        )


    if capability_attention_count:
        limitations.append(
            "The capability registry identified "
            f"{capability_attention_count} source(s) requiring attention, "
            "an adapter, async probing, or implementation verification."
        )

    if not limitations:
        limitations.append(
            "The available evidence does not prove a specific defect. "
            "The next changes should therefore be driven by focused runtime "
            "measurements and failing qualification tests rather than guesses."
        )

    priorities = [
        (
            "Keep developer and self-evaluation responses deterministic and "
            "evidence-backed so Neuro cannot invent files, test results, "
            "provider activity, or completed capabilities."
        ),
        (
            "Expose intent family, subtype, and grounding state in internal "
            "runtime metadata so developer-mode behavior can be qualified "
            "without changing the public response contract."
        ),
        (
            "Inspect the highest-connectivity repository hotspots individually "
            "before splitting orchestration responsibilities or moving files."
        ),
        (
            "Add capability-state evidence for market data, portfolio, risk, "
            "paper trading, SnapTrade, repository intelligence, and future "
            "Cerberus services."
        ),
        (
            "Measure prompt size, model latency, and response grounding as "
            "separate qualification signals."
        ),
    ]

    missing_evidence = [
        (
            "Current focused test results are not loaded by this response "
            "builder, so it will not claim that any broader subsystem is "
            "fully tested."
        ),
        (
            "No live provider, broker, market-feed, or external-service "
            "execution evidence was supplied to this response."
        ),
        (
            "Repository indexes and architecture dashboards describe structure; "
            "they do not by themselves prove runtime correctness or performance."
        ),
    ]

    if loader_errors:
        missing_evidence.append(
            "Loader errors encountered: "
            + "; ".join(loader_errors[:4])
        )

    heading = (
        "Developer self-evaluation"
        if subtype == "self_evaluation"
        else "Developer architecture review"
        if subtype == "architecture_review"
        else "Developer review"
    )

    return (
        f"## {heading}\n\n"
        "### What the current evidence proves\n"
        f"{_bullet_lines(proven)}\n\n"
        "### Proven limitations or boundaries\n"
        f"{_bullet_lines(limitations)}\n\n"
        "### Capability state\n"
        f"{_bullet_lines(capability_lines)}\n\n"
        "### Highest-impact next improvements\n"
        f"{_bullet_lines(priorities)}\n\n"
        "### Evidence still missing\n"
        f"{_bullet_lines(missing_evidence)}\n\n"
        "I have not claimed that tests ran, providers responded, market data "
        "was refreshed, or broker operations occurred unless those facts were "
        "present in the loaded evidence."
    )


__all__ = [
    "build_developer_response",
]
