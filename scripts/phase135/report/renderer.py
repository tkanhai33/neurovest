#!/usr/bin/env python3

"""
Console renderer for Phase 135 audit results.
"""

from __future__ import annotations

from typing import Any


def render_repository_discovery(report: dict[str, Any]) -> str:
    discovery = report["discovery"]
    discovery_summary = discovery["summary"]

    layer_mapping = report.get("layer_mapping", {})
    layer_summary = layer_mapping.get("summary", {})

    lines: list[str] = []

    lines.append("=" * 80)
    lines.append("PHASE 135")
    lines.append("NEUROVEST BLIND PRODUCTION READINESS AUDIT")
    lines.append("=" * 80)
    lines.append("")
    lines.append("AUDIT MODE")
    lines.append(str(report["audit_mode"]).upper())
    lines.append("")
    lines.append("COMPLETED STAGES")

    for stage in report.get("completed_stages", []):
        lines.append(f"- {stage}")

    lines.append("")
    lines.append("REPOSITORY")
    lines.append(discovery["repository_root"])
    lines.append("")
    lines.append("REPOSITORY DISCOVERY")
    lines.append(
        f"Files discovered:              {discovery_summary['total_files']}"
    )
    lines.append(
        f"Directories discovered:        {discovery_summary['total_directories']}"
    )
    lines.append(
        f"Repository bytes inspected:    {discovery_summary['total_bytes']}"
    )
    lines.append(
        f"Source files:                  {discovery_summary['source_files']}"
    )
    lines.append(
        f"Test files:                    {discovery_summary['test_files']}"
    )
    lines.append(
        f"Configuration files:           {discovery_summary['config_files']}"
    )
    lines.append(
        f"Entrypoint candidates:         "
        f"{discovery_summary['entrypoint_candidates']}"
    )
    lines.append(
        f"Duplicate file groups:         "
        f"{discovery_summary['duplicate_file_groups']}"
    )

    lines.append("")
    lines.append("LAYER MAPPING")
    lines.append("Architecture assumed:          NO")
    lines.append(
        f"Package roots:                 {layer_summary.get('package_roots', 0)}"
    )
    lines.append(
        f"Source roots:                  {layer_summary.get('source_roots', 0)}"
    )
    lines.append(
        f"Repository regions:            "
        f"{layer_summary.get('repository_regions', 0)}"
    )
    lines.append(
        f"Candidate layers:              "
        f"{layer_summary.get('candidate_layers', 0)}"
    )
    lines.append(
        f"Framework signals:             "
        f"{layer_summary.get('framework_signals', 0)}"
    )
    lines.append(
        f"Boundary signals:              "
        f"{layer_summary.get('boundary_signals', 0)}"
    )
    lines.append(
        f"Ambiguous source regions:      "
        f"{layer_summary.get('ambiguous_regions', 0)}"
    )

    lines.append("")
    lines.append("CANDIDATE LAYER SOURCE COUNTS")

    candidate_layers = layer_mapping.get("candidate_layers", [])

    if candidate_layers:
        ordered_layers = sorted(
            candidate_layers,
            key=lambda item: (
                -item["source_file_count"],
                item["layer"],
            ),
        )

        for layer in ordered_layers:
            lines.append(
                f"{layer['layer']:<36} "
                f"{layer['source_file_count']:>6} source files"
            )
    else:
        lines.append("No candidate layers discovered.")

    lines.append("")
    lines.append("SOURCE OWNERSHIP ESTIMATE")

    ownership = (
        layer_mapping
        .get("ownership_summary", {})
        .get("source_ownership_estimate", {})
    )

    lines.append(
        "Active source files:                    "
        f"{ownership.get('active_source_files', 0)}"
    )
    lines.append(
        "Archived or quarantined source files:   "
        f"{ownership.get('archived_or_quarantined_source_files', 0)}"
    )
    lines.append(
        "Generated or report source files:       "
        f"{ownership.get('generated_or_report_source_files', 0)}"
    )

    lines.append("")
    lines.append("FRAMEWORK SIGNALS")

    framework_signals = layer_mapping.get("framework_signals", [])

    if framework_signals:
        for signal in framework_signals:
            lines.append(
                f"- {signal['framework_or_system']} "
                f"[{signal['confidence']}]"
            )
    else:
        lines.append("No framework signals discovered.")

    lines.append("")
    lines.append("AMBIGUOUS SOURCE REGIONS")

    ambiguous_regions = layer_mapping.get("ambiguous_regions", [])

    if ambiguous_regions:
        for item in ambiguous_regions[:30]:
            lines.append(
                f"- {item['path']} "
                f"({item['direct_source_file_count']} direct source files)"
            )

        if len(ambiguous_regions) > 30:
            lines.append(
                f"... and {len(ambiguous_regions) - 30} more"
            )
    else:
        lines.append("No ambiguous source-bearing directories discovered.")

    lines.append("")
    lines.append("DEPENDENCY MAPPING")

    dependency_mapping = report.get("dependency_mapping", {})
    dependency_summary = dependency_mapping.get("summary", {})

    lines.append(
        "Python files analyzed:                   "
        f"{dependency_summary.get('python_files_analyzed', 0)}"
    )
    lines.append(
        "JavaScript/TypeScript files analyzed:    "
        f"{dependency_summary.get('javascript_files_analyzed', 0)}"
    )
    lines.append(
        "Internal dependency edges:               "
        f"{dependency_summary.get('internal_dependency_edges', 0)}"
    )
    lines.append(
        "Active internal edges:                   "
        f"{dependency_summary.get('active_internal_edges', 0)}"
    )
    lines.append(
        "Archived or generated edges:             "
        f"{dependency_summary.get('archived_or_generated_edges', 0)}"
    )
    lines.append(
        "External dependencies:                   "
        f"{dependency_summary.get('external_dependencies', 0)}"
    )
    lines.append(
        "Unresolved dependencies:                 "
        f"{dependency_summary.get('unresolved_dependencies', 0)}"
    )
    lines.append(
        "Dependency cycles:                       "
        f"{dependency_summary.get('dependency_cycles', 0)}"
    )
    lines.append(
        "Graph nodes:                             "
        f"{dependency_summary.get('graph_nodes', 0)}"
    )

    lines.append("")
    lines.append("TOP INBOUND DEPENDENCIES")

    top_inbound = (
        dependency_mapping
        .get("graph_metrics", {})
        .get("top_inbound_files", [])
    )

    if top_inbound:
        for item in top_inbound[:15]:
            lines.append(
                f"- {item['path']} "
                f"({item['incoming_dependencies']} incoming)"
            )
    else:
        lines.append("No inbound dependency data discovered.")

    lines.append("")
    lines.append("DEPENDENCY CYCLES")

    cycles = dependency_mapping.get("cycles", [])

    if cycles:
        for index, cycle in enumerate(cycles[:10], start=1):
            lines.append(
                f"- Cycle {index}: {cycle['node_count']} nodes"
            )

            for node in cycle["nodes"][:10]:
                lines.append(f"    {node}")

            if len(cycle["nodes"]) > 10:
                lines.append(
                    f"    ... and {len(cycle['nodes']) - 10} more"
                )

        if len(cycles) > 10:
            lines.append(f"... and {len(cycles) - 10} more cycles")
    else:
        lines.append("No static dependency cycles discovered.")

    lines.append("")
    lines.append("IMPORT GRAPH NORMALIZATION")

    import_graph = report.get("import_graph", {})
    import_summary = import_graph.get("summary", {})

    lines.append(
        "File nodes:                              "
        f"{import_summary.get('file_nodes', 0)}"
    )
    lines.append(
        "Module nodes:                            "
        f"{import_summary.get('module_nodes', 0)}"
    )
    lines.append(
        "Package nodes:                           "
        f"{import_summary.get('package_nodes', 0)}"
    )
    lines.append(
        "Normalized file edges:                   "
        f"{import_summary.get('normalized_file_edges', 0)}"
    )
    lines.append(
        "Module edges:                            "
        f"{import_summary.get('module_edges', 0)}"
    )
    lines.append(
        "Package edges:                           "
        f"{import_summary.get('package_edges', 0)}"
    )
    lines.append(
        "Active file edges:                       "
        f"{import_summary.get('active_file_edges', 0)}"
    )
    lines.append(
        "Non-active file edges:                   "
        f"{import_summary.get('non_active_file_edges', 0)}"
    )
    lines.append(
        "Self edges:                              "
        f"{import_summary.get('self_edges', 0)}"
    )
    lines.append(
        "Unresolved groups:                       "
        f"{import_summary.get('unresolved_groups', 0)}"
    )
    lines.append(
        "Package cycles:                          "
        f"{import_summary.get('package_cycles', 0)}"
    )

    lines.append("")
    lines.append("TOP PACKAGE FAN-IN")

    top_package_inbound = (
        import_graph
        .get("package_graph", {})
        .get("metrics", {})
        .get("top_inbound", [])
    )

    if top_package_inbound:
        for item in top_package_inbound[:15]:
            lines.append(
                f"- {item['id']} ({item['in_degree']} incoming)"
            )
    else:
        lines.append("No package fan-in data discovered.")

    lines.append("")
    lines.append("TOP PACKAGE FAN-OUT")

    top_package_outbound = (
        import_graph
        .get("package_graph", {})
        .get("metrics", {})
        .get("top_outbound", [])
    )

    if top_package_outbound:
        for item in top_package_outbound[:15]:
            lines.append(
                f"- {item['id']} ({item['out_degree']} outgoing)"
            )
    else:
        lines.append("No package fan-out data discovered.")

    lines.append("")
    lines.append("PACKAGE CYCLES")

    package_cycles = (
        import_graph
        .get("package_graph", {})
        .get("cycles", [])
    )

    if package_cycles:
        for index, cycle in enumerate(package_cycles[:10], start=1):
            lines.append(
                f"- Package cycle {index}: "
                f"{cycle['node_count']} packages"
            )

            for node in cycle["nodes"]:
                lines.append(f"    {node}")
    else:
        lines.append("No package-level cycles discovered.")

    lines.append("")
    lines.append("RUNTIME GRAPH DISCOVERY")

    runtime_graph = report.get("runtime_graph", {})
    runtime_summary = runtime_graph.get("summary", {})

    lines.append(
        "Application executed:                    NO"
    )
    lines.append(
        "Entrypoints:                             "
        f"{runtime_summary.get('entrypoints', 0)}"
    )
    lines.append(
        "Active entrypoints:                      "
        f"{runtime_summary.get('active_entrypoints', 0)}"
    )
    lines.append(
        "Non-active entrypoints:                  "
        f"{runtime_summary.get('non_active_entrypoints', 0)}"
    )
    lines.append(
        "Routes discovered:                       "
        f"{runtime_summary.get('routes', 0)}"
    )
    lines.append(
        "Runtime signals:                         "
        f"{runtime_summary.get('runtime_signals', 0)}"
    )
    lines.append(
        "Runtime edges:                           "
        f"{runtime_summary.get('runtime_edges', 0)}"
    )
    lines.append(
        "Runtime cycles:                          "
        f"{runtime_summary.get('runtime_cycles', 0)}"
    )
    lines.append(
        "Reachable files:                         "
        f"{runtime_summary.get('reachable_files', 0)}"
    )
    lines.append(
        "Unreachable active files:                "
        f"{runtime_summary.get('unreachable_active_files', 0)}"
    )
    lines.append(
        "Parse errors:                            "
        f"{runtime_summary.get('parse_errors', 0)}"
    )

    lines.append("")
    lines.append("ACTIVE ENTRYPOINTS")

    active_entrypoints = runtime_graph.get(
        "active_entrypoints",
        [],
    )

    if active_entrypoints:
        for item in active_entrypoints[:30]:
            lines.append(
                f"- {item['source']} "
                f"[{item['entrypoint_type']}]"
            )

        if len(active_entrypoints) > 30:
            lines.append(
                f"... and {len(active_entrypoints) - 30} more"
            )
    else:
        lines.append("No active entrypoints discovered.")

    lines.append("")
    lines.append("ROUTE COUNTS")

    route_counts = runtime_graph.get("route_counts", {})

    if route_counts:
        for framework, count in route_counts.items():
            lines.append(f"- {framework}: {count}")
    else:
        lines.append("No framework routes discovered.")

    lines.append("")
    lines.append("RUNTIME SIGNAL COUNTS")

    signal_counts = runtime_graph.get("signal_counts", {})

    if signal_counts:
        for signal_type, count in list(
            signal_counts.items()
        )[:20]:
            lines.append(f"- {signal_type}: {count}")
    else:
        lines.append("No runtime signals discovered.")

    lines.append("")
    lines.append("ENTRYPOINT REACHABILITY")

    reachability = runtime_graph.get("reachability", {})

    for item in reachability.get("by_entrypoint", [])[:20]:
        lines.append(
            f"- {item['entrypoint']}: "
            f"{item['reachable_file_count']} files"
        )

    if not reachability.get("by_entrypoint"):
        lines.append("No entrypoint reachability data discovered.")

    lines.append("")
    lines.append("CONTRACT DISCOVERY")

    contract_discovery = report.get(
        "contract_discovery",
        {},
    )
    contract_summary = contract_discovery.get(
        "summary",
        {},
    )

    lines.append(
        "Application executed:                    NO"
    )
    lines.append(
        "Contracts discovered:                    "
        f"{contract_summary.get('contracts', 0)}"
    )
    lines.append(
        "Active contracts:                        "
        f"{contract_summary.get('active_contracts', 0)}"
    )
    lines.append(
        "Non-active contracts:                    "
        f"{contract_summary.get('non_active_contracts', 0)}"
    )
    lines.append(
        "Contract files:                          "
        f"{contract_summary.get('contract_files', 0)}"
    )
    lines.append(
        "Active contract files:                   "
        f"{contract_summary.get('active_contract_files', 0)}"
    )
    lines.append(
        "Function contracts:                      "
        f"{contract_summary.get('function_contracts', 0)}"
    )
    lines.append(
        "Route contracts:                         "
        f"{contract_summary.get('route_contracts', 0)}"
    )
    lines.append(
        "Safety signals:                          "
        f"{contract_summary.get('safety_signals', 0)}"
    )
    lines.append(
        "Safety files:                            "
        f"{contract_summary.get('safety_files', 0)}"
    )
    lines.append(
        "Duplicate contract names:                "
        f"{contract_summary.get('duplicate_contract_names', 0)}"
    )
    lines.append(
        "Parse errors:                            "
        f"{contract_summary.get('parse_errors', 0)}"
    )

    lines.append("")
    lines.append("CONTRACT KIND COUNTS")

    contract_kind_counts = contract_discovery.get(
        "contract_kind_counts",
        {},
    )

    if contract_kind_counts:
        for kind, count in contract_kind_counts.items():
            lines.append(f"- {kind}: {count}")
    else:
        lines.append("No contract kinds discovered.")

    lines.append("")
    lines.append("ROUTE CONTRACT COVERAGE")

    route_coverage = contract_discovery.get(
        "route_contract_coverage",
        {},
    )

    lines.append(
        "Total routes:                            "
        f"{route_coverage.get('total_routes', 0)}"
    )
    lines.append(
        "Routes with request models:               "
        f"{route_coverage.get('routes_with_request_models', 0)}"
    )
    lines.append(
        "Routes with response models:              "
        f"{route_coverage.get('routes_with_response_models', 0)}"
    )
    lines.append(
        "Routes with return annotations:           "
        f"{route_coverage.get('routes_with_return_annotations', 0)}"
    )
    lines.append(
        "Routes without explicit contracts:        "
        f"{route_coverage.get('routes_without_explicit_contract', 0)}"
    )
    lines.append(
        "Explicit contract coverage:               "
        f"{route_coverage.get('explicit_contract_coverage_percent', 0.0)}%"
    )

    lines.append("")
    lines.append("DUPLICATE CONTRACT NAMES")

    duplicate_names = contract_discovery.get(
        "duplicate_contract_names",
        [],
    )

    if duplicate_names:
        for item in duplicate_names[:20]:
            lines.append(
                f"- {item['name']}: "
                f"{item['declaration_count']} declarations "
                f"across {item['source_count']} files"
            )

        if len(duplicate_names) > 20:
            lines.append(
                f"... and {len(duplicate_names) - 20} more"
            )
    else:
        lines.append("No duplicate contract names discovered.")

    lines.append("")
    lines.append("FINTECH CAPABILITY GRADING")

    fintech = report.get(
        "fintech_capability",
        {},
    )

    fintech_summary = fintech.get(
        "summary",
        {},
    )

    lines.append(
        "Application executed:                    NO"
    )
    lines.append(
        "Repository rescanned by grader:           NO"
    )
    lines.append(
        "Production readiness assessed:            NO"
    )
    lines.append(
        "Production blockers assessed:             NO"
    )
    lines.append(
        "Categories graded:                        "
        f"{fintech_summary.get('category_count', 0)}"
    )
    lines.append(
        "Capability score:                         "
        f"{fintech_summary.get('total_score', 0.0)}"
        f"/{fintech_summary.get('total_maximum', 0)}"
    )
    lines.append(
        "Capability percentage:                    "
        f"{fintech_summary.get('percentage', 0.0)}%"
    )
    lines.append(
        "Capability status:                        "
        f"{fintech_summary.get('status', 'Unknown')}"
    )
    lines.append(
        "Checks passed:                            "
        f"{fintech_summary.get('checks_passed', 0)}"
        f"/{fintech_summary.get('checks_total', 0)}"
    )
    lines.append(
        "Capability gaps:                          "
        f"{fintech_summary.get('capability_gaps', 0)}"
    )

    lines.append("")
    lines.append("FINTECH CATEGORY SCORES")

    categories = fintech.get(
        "categories",
        [],
    )

    if categories:
        for category in categories:
            lines.append(
                f"{category['category']:<36} "
                f"{category['score']:>6.1f}/"
                f"{category['maximum']:<5.1f} "
                f"{category['percentage']:>6.2f}% "
                f"[{category['status']}]"
            )
    else:
        lines.append(
            "No fintech capability categories were graded."
        )

    lines.append("")
    lines.append("STRONGEST FINTECH CATEGORIES")

    strongest = fintech.get(
        "strongest_categories",
        [],
    )

    if strongest:
        for item in strongest:
            lines.append(
                f"- {item['category']}: "
                f"{item['percentage']}% "
                f"[{item['status']}]"
            )
    else:
        lines.append(
            "No strongest-category evidence available."
        )

    lines.append("")
    lines.append("WEAKEST FINTECH CATEGORIES")

    weakest = fintech.get(
        "weakest_categories",
        [],
    )

    if weakest:
        for item in weakest:
            lines.append(
                f"- {item['category']}: "
                f"{item['percentage']}% "
                f"[{item['status']}]"
            )
    else:
        lines.append(
            "No weakest-category evidence available."
        )

    lines.append("")
    lines.append("FINTECH CAPABILITY GAPS")

    capability_gaps = fintech.get(
        "capability_gaps",
        [],
    )

    if capability_gaps:
        for item in capability_gaps[:30]:
            lines.append(
                f"- {item['category']}: "
                f"{item['check']}"
            )

        if len(capability_gaps) > 30:
            lines.append(
                f"... and {len(capability_gaps) - 30} more"
            )
    else:
        lines.append(
            "No fintech capability gaps were identified."
        )

    lines.append("")
    lines.append("AI CAPABILITY GRADING")

    ai_capability = report.get(
        "ai_capability",
        {},
    )

    ai_summary = ai_capability.get(
        "summary",
        {},
    )

    lines.append(
        "Application executed:                    NO"
    )
    lines.append(
        "Repository rescanned by grader:           NO"
    )
    lines.append(
        "Fintech score modified:                   NO"
    )
    lines.append(
        "Production readiness assessed:            NO"
    )
    lines.append(
        "Production blockers assessed:             NO"
    )
    lines.append(
        "Categories graded:                        "
        f"{ai_summary.get('category_count', 0)}"
    )
    lines.append(
        "Capability score:                         "
        f"{ai_summary.get('total_score', 0.0)}"
        f"/{ai_summary.get('total_maximum', 0)}"
    )
    lines.append(
        "Capability percentage:                    "
        f"{ai_summary.get('percentage', 0.0)}%"
    )
    lines.append(
        "Capability status:                        "
        f"{ai_summary.get('status', 'Unknown')}"
    )
    lines.append(
        "Checks passed:                            "
        f"{ai_summary.get('checks_passed', 0)}"
        f"/{ai_summary.get('checks_total', 0)}"
    )
    lines.append(
        "Capability gaps:                          "
        f"{ai_summary.get('capability_gaps', 0)}"
    )

    lines.append("")
    lines.append("AI CATEGORY SCORES")

    ai_categories = ai_capability.get(
        "categories",
        [],
    )

    if ai_categories:
        for category in ai_categories:
            lines.append(
                f"{category['category']:<40} "
                f"{category['score']:>6.1f}/"
                f"{category['maximum']:<5.1f} "
                f"{category['percentage']:>6.2f}% "
                f"[{category['status']}]"
            )
    else:
        lines.append(
            "No AI capability categories were graded."
        )

    lines.append("")
    lines.append("STRONGEST AI CATEGORIES")

    strongest_ai = ai_capability.get(
        "strongest_categories",
        [],
    )

    if strongest_ai:
        for item in strongest_ai:
            lines.append(
                f"- {item['category']}: "
                f"{item['percentage']}% "
                f"[{item['status']}]"
            )
    else:
        lines.append(
            "No strongest-category evidence available."
        )

    lines.append("")
    lines.append("WEAKEST AI CATEGORIES")

    weakest_ai = ai_capability.get(
        "weakest_categories",
        [],
    )

    if weakest_ai:
        for item in weakest_ai:
            lines.append(
                f"- {item['category']}: "
                f"{item['percentage']}% "
                f"[{item['status']}]"
            )
    else:
        lines.append(
            "No weakest-category evidence available."
        )

    lines.append("")
    lines.append("AI CAPABILITY GAPS")

    ai_gaps = ai_capability.get(
        "capability_gaps",
        [],
    )

    if ai_gaps:
        for item in ai_gaps[:30]:
            lines.append(
                f"- {item['category']}: "
                f"{item['check']}"
            )

        if len(ai_gaps) > 30:
            lines.append(
                f"... and {len(ai_gaps) - 30} more"
            )
    else:
        lines.append(
            "No AI capability gaps were identified."
        )

    lines.append("")
    lines.append("PRODUCTION READINESS GRADING")

    readiness = report.get(
        "production_readiness",
        {},
    )

    readiness_summary = readiness.get(
        "summary",
        {},
    )

    lines.append(
        "Application executed:                    NO"
    )
    lines.append(
        "Repository rescanned by grader:           NO"
    )
    lines.append(
        "Fintech score modified:                   NO"
    )
    lines.append(
        "AI score modified:                        NO"
    )
    lines.append(
        "Production blockers assessed:             NO"
    )
    lines.append(
        "Deployment approved:                      NO"
    )
    lines.append(
        "Live trading approved:                    NO"
    )
    lines.append(
        "Categories graded:                        "
        f"{readiness_summary.get('category_count', 0)}"
    )
    lines.append(
        "Readiness score:                          "
        f"{readiness_summary.get('total_score', 0.0)}"
        f"/{readiness_summary.get('total_maximum', 0)}"
    )
    lines.append(
        "Readiness percentage:                     "
        f"{readiness_summary.get('percentage', 0.0)}%"
    )
    lines.append(
        "Readiness status:                         "
        f"{readiness_summary.get('status', 'Unknown')}"
    )
    lines.append(
        "Checks passed:                            "
        f"{readiness_summary.get('checks_passed', 0)}"
        f"/{readiness_summary.get('checks_total', 0)}"
    )
    lines.append(
        "Readiness gaps:                           "
        f"{readiness_summary.get('readiness_gaps', 0)}"
    )

    lines.append("")
    lines.append("PRODUCTION READINESS CATEGORY SCORES")

    readiness_categories = readiness.get(
        "categories",
        [],
    )

    if readiness_categories:
        for category in readiness_categories:
            lines.append(
                f"{category['category']:<40} "
                f"{category['score']:>6.1f}/"
                f"{category['maximum']:<5.1f} "
                f"{category['percentage']:>6.2f}% "
                f"[{category['status']}]"
            )
    else:
        lines.append(
            "No production-readiness categories were graded."
        )

    lines.append("")
    lines.append("STRONGEST READINESS CATEGORIES")

    strongest_readiness = readiness.get(
        "strongest_categories",
        [],
    )

    if strongest_readiness:
        for item in strongest_readiness:
            lines.append(
                f"- {item['category']}: "
                f"{item['percentage']}% "
                f"[{item['status']}]"
            )
    else:
        lines.append(
            "No strongest readiness categories available."
        )

    lines.append("")
    lines.append("WEAKEST READINESS CATEGORIES")

    weakest_readiness = readiness.get(
        "weakest_categories",
        [],
    )

    if weakest_readiness:
        for item in weakest_readiness:
            lines.append(
                f"- {item['category']}: "
                f"{item['percentage']}% "
                f"[{item['status']}]"
            )
    else:
        lines.append(
            "No weakest readiness categories available."
        )

    lines.append("")
    lines.append("PRODUCTION READINESS GAPS")

    readiness_gaps = readiness.get(
        "readiness_gaps",
        [],
    )

    if readiness_gaps:
        for item in readiness_gaps[:40]:
            lines.append(
                f"- {item['category']}: "
                f"{item['check']}"
            )

        if len(readiness_gaps) > 40:
            lines.append(
                f"... and {len(readiness_gaps) - 40} more"
            )
    else:
        lines.append(
            "No production-readiness gaps identified."
        )

    lines.append("")
    lines.append("PRODUCTION BLOCKER GRADING")

    blockers = report.get(
        "production_blockers",
        {},
    )

    blocker_summary = blockers.get(
        "summary",
        {},
    )

    lines.append(
        "Application executed:                    NO"
    )
    lines.append(
        "Repository rescanned by grader:           NO"
    )
    lines.append(
        "Fintech score modified:                   NO"
    )
    lines.append(
        "AI score modified:                        NO"
    )
    lines.append(
        "Readiness score modified:                 NO"
    )
    lines.append(
        "Deployment approved:                      NO"
    )
    lines.append(
        "Live trading approved:                    NO"
    )
    lines.append(
        "Overall blocker status:                   "
        f"{blocker_summary.get('overall_status', 'UNKNOWN')}"
    )
    lines.append(
        "Total findings:                           "
        f"{blocker_summary.get('finding_count', 0)}"
    )
    lines.append(
        "Blocking findings:                        "
        f"{blocker_summary.get('blocking_finding_count', 0)}"
    )
    lines.append(
        "Critical blockers:                        "
        f"{blocker_summary.get('critical_blockers', 0)}"
    )
    lines.append(
        "High blockers:                            "
        f"{blocker_summary.get('high_blockers', 0)}"
    )
    lines.append(
        "Deferred integrations:                    "
        f"{blocker_summary.get('deferred_integrations', 0)}"
    )
    lines.append(
        "Maturity gaps:                            "
        f"{blocker_summary.get('maturity_gaps', 0)}"
    )
    lines.append(
        "Informational findings:                   "
        f"{blocker_summary.get('informational_findings', 0)}"
    )

    lines.append("")
    lines.append("CRITICAL BLOCKERS")

    critical_blockers = blockers.get(
        "critical_blockers",
        [],
    )

    if critical_blockers:
        for item in critical_blockers:
            lines.append(
                f"- [{item['domain']}] {item['title']}"
            )
    else:
        lines.append(
            "No critical blockers identified."
        )

    lines.append("")
    lines.append("HIGH BLOCKERS")

    high_blockers = blockers.get(
        "high_blockers",
        [],
    )

    if high_blockers:
        for item in high_blockers[:30]:
            lines.append(
                f"- [{item['domain']}] {item['title']}"
            )

        if len(high_blockers) > 30:
            lines.append(
                f"... and {len(high_blockers) - 30} more"
            )
    else:
        lines.append(
            "No high blockers identified."
        )

    lines.append("")
    lines.append("DEFERRED INTEGRATIONS")

    deferred = blockers.get(
        "deferred_integrations",
        [],
    )

    if deferred:
        for item in deferred:
            lines.append(
                f"- [{item['domain']}] {item['title']}"
            )
    else:
        lines.append(
            "No deferred integrations identified."
        )

    lines.append("")
    lines.append("MATURITY GAPS")

    maturity = blockers.get(
        "maturity_gaps",
        [],
    )

    if maturity:
        for item in maturity[:30]:
            lines.append(
                f"- [{item['domain']}] {item['title']}"
            )

        if len(maturity) > 30:
            lines.append(
                f"... and {len(maturity) - 30} more"
            )
    else:
        lines.append(
            "No maturity gaps identified."
        )

    lines.append("")
    lines.append("MODE ELIGIBILITY")

    eligibility = blockers.get(
        "eligibility",
        {},
    )

    for mode_key, label in [
        ("paper_mode", "Paper mode"),
        (
            "authenticated_broker_integration",
            "Authenticated broker integration",
        ),
        ("live_trading", "Live trading"),
    ]:
        mode = eligibility.get(
            mode_key,
            {},
        )

        lines.append(
            f"{label:<40} "
            f"eligible={str(mode.get('eligible', False)).upper()} "
            f"approved={str(mode.get('approved', False)).upper()} "
            f"blockers={len(mode.get('blocking_findings', []))}"
        )

    lines.append("")
    lines.append("TOP REMEDIATION ORDER")

    remediation_order = blockers.get(
        "remediation_order",
        [],
    )

    if remediation_order:
        for item in remediation_order[:25]:
            lines.append(
                f"{item['order']:>2}. "
                f"[{item['classification']}] "
                f"{item['title']}"
            )

        if len(remediation_order) > 25:
            lines.append(
                f"... and {len(remediation_order) - 25} more"
            )
    else:
        lines.append(
            "No remediation items generated."
        )

    lines.append("")
    lines.append("FINAL AUDIT REPORT")

    final_report = report.get(
        "final_report",
        {},
    )

    executive = final_report.get(
        "executive_summary",
        {},
    )

    lines.append(
        "Raw findings:                            "
        f"{final_report.get('raw_finding_count', 0)}"
    )
    lines.append(
        "Root workstreams:                         "
        f"{final_report.get('root_workstream_count', 0)}"
    )
    lines.append(
        "Duplicate findings consolidated:          "
        f"{final_report.get('duplicate_reduction', 0)}"
    )
    lines.append(
        "Critical root workstreams:                "
        f"{executive.get('critical_workstreams', 0)}"
    )
    lines.append(
        "High root workstreams:                    "
        f"{executive.get('high_workstreams', 0)}"
    )
    lines.append(
        "Deferred root workstreams:                "
        f"{executive.get('deferred_workstreams', 0)}"
    )
    lines.append(
        "Maturity root workstreams:                "
        f"{executive.get('maturity_workstreams', 0)}"
    )

    lines.append("")
    lines.append("ROOT WORKSTREAM ORDER")

    for item in final_report.get(
        "root_workstreams",
        [],
    ):
        lines.append(
            f"{item['order']:>2}. "
            f"[{item['classification']}] "
            f"{item['title']}"
        )

    lines.append("")
    lines.append("FINAL MODE STATUS")

    final_status = final_report.get(
        "final_status",
        {},
    )

    for mode_key, label in [
        ("paper_mode", "Paper mode"),
        (
            "authenticated_broker",
            "Authenticated broker",
        ),
        ("live_trading", "Live trading"),
    ]:
        mode = final_status.get(
            mode_key,
            {},
        )

        lines.append(
            f"{label:<40} "
            f"{mode.get('status', 'UNKNOWN')} "
            f"workstreams={mode.get('remaining_workstreams', 0)} "
            f"approved={str(mode.get('approved', False)).upper()}"
        )

    lines.append("")
    lines.append("OUTPUT")
    lines.append("runtime/audits/latest.json")
    lines.append("runtime/audits/final_report_latest.json")
    lines.append("runtime/audits/final_report_latest.txt")
    lines.append("runtime/audits/history/<timestamp>.json")
    lines.append("")
    lines.append("GRADING")
    lines.append("Production readiness grading completed.")
    lines.append("Production blocker grading completed.")
    lines.append("Deployment remains unapproved.")
    lines.append("Live trading remains unapproved.")
    lines.append("")
    lines.append("NEXT")
    lines.append("Implement Phase 135 Freeze Verification")
    lines.append("")
    lines.append("=" * 80)

    return "\n".join(lines)
