#!/usr/bin/env python3

"""
Phase 135 audit orchestration.

Stages 1-6:
    Discovery and graph analysis.

Stage 7:
    Fintech capability grading.

Stage 8:
    AI capability grading.

Stage 9:
    Production readiness grading.

Stage 10:
    Production blocker grading.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from scripts.phase135.discovery.contract_discovery import ContractDiscovery
from scripts.phase135.discovery.dependency_mapper import DependencyMapper
from scripts.phase135.discovery.layer_mapper import LayerMapper
from scripts.phase135.discovery.repository_scanner import RepositoryScanner
from scripts.phase135.grading.ai_grader import AICapabilityGrader
from scripts.phase135.grading.blocker_grader import ProductionBlockerGrader
from scripts.phase135.grading.fintech_grader import FintechCapabilityGrader
from scripts.phase135.grading.production_grader import ProductionReadinessGrader
from scripts.phase135.graph.import_graph import ImportGraphNormalizer
from scripts.phase135.graph.runtime_graph import RuntimeGraphDiscovery
from scripts.phase135.report.final_report import FinalAuditReportBuilder


class AuditEngine:
    """
    Coordinate independent Phase 135 audit stages.
    """

    def __init__(
        self,
        repository_root: Path,
    ) -> None:
        self.repository_root = repository_root.resolve()

    def run_repository_discovery(
        self,
    ) -> dict[str, Any]:
        started_at = datetime.now(UTC)

        discovery = RepositoryScanner(
            self.repository_root
        ).scan()

        layer_mapping = LayerMapper(
            repository_root=self.repository_root,
            discovery=discovery,
        ).map_layers()

        dependency_mapping = DependencyMapper(
            repository_root=self.repository_root,
            discovery=discovery,
            layer_mapping=layer_mapping,
        ).map_dependencies()

        import_graph = ImportGraphNormalizer(
            repository_root=self.repository_root,
            discovery=discovery,
            layer_mapping=layer_mapping,
            dependency_mapping=dependency_mapping,
        ).normalize()

        runtime_graph = RuntimeGraphDiscovery(
            repository_root=self.repository_root,
            discovery=discovery,
            dependency_mapping=dependency_mapping,
            import_graph=import_graph,
        ).discover()

        contract_discovery = ContractDiscovery(
            repository_root=self.repository_root,
            discovery=discovery,
            runtime_graph=runtime_graph,
        ).discover()

        fintech_capability = FintechCapabilityGrader(
            discovery=discovery,
            layer_mapping=layer_mapping,
            dependency_mapping=dependency_mapping,
            import_graph=import_graph,
            runtime_graph=runtime_graph,
            contract_discovery=contract_discovery,
        ).grade()

        ai_capability = AICapabilityGrader(
            discovery=discovery,
            layer_mapping=layer_mapping,
            dependency_mapping=dependency_mapping,
            import_graph=import_graph,
            runtime_graph=runtime_graph,
            contract_discovery=contract_discovery,
            fintech_capability=fintech_capability,
        ).grade()

        production_readiness = ProductionReadinessGrader(
            discovery=discovery,
            layer_mapping=layer_mapping,
            dependency_mapping=dependency_mapping,
            import_graph=import_graph,
            runtime_graph=runtime_graph,
            contract_discovery=contract_discovery,
            fintech_capability=fintech_capability,
            ai_capability=ai_capability,
        ).grade()

        production_blockers = ProductionBlockerGrader(
            discovery=discovery,
            layer_mapping=layer_mapping,
            dependency_mapping=dependency_mapping,
            import_graph=import_graph,
            runtime_graph=runtime_graph,
            contract_discovery=contract_discovery,
            fintech_capability=fintech_capability,
            ai_capability=ai_capability,
            production_readiness=production_readiness,
        ).grade()

        partial_audit = {
            "phase": 135,
            "discovery": discovery,
            "layer_mapping": layer_mapping,
            "dependency_mapping": dependency_mapping,
            "import_graph": import_graph,
            "runtime_graph": runtime_graph,
            "contract_discovery": contract_discovery,
            "fintech_capability": fintech_capability,
            "ai_capability": ai_capability,
            "production_readiness": production_readiness,
            "production_blockers": production_blockers,
        }

        final_report = FinalAuditReportBuilder(
            partial_audit
        ).build()

        completed_at = datetime.now(UTC)

        return {
            "phase": 135,
            "audit_name": (
                "NeuroVest Blind Production Readiness Audit"
            ),
            "audit_mode": "read_only",
            "audit_stage": (
                "repository_discovery_layer_mapping_dependency_mapping_"
                "import_graph_normalization_runtime_graph_discovery_"
                "contract_discovery_fintech_capability_grading_"
                "ai_capability_grading_production_readiness_grading_"
                "production_blocker_grading"
            ),
            "completed_stages": [
                "repository_discovery",
                "layer_mapping",
                "dependency_mapping",
                "import_graph_normalization",
                "runtime_graph_discovery",
                "contract_discovery",
                "fintech_capability_grading",
                "ai_capability_grading",
                "production_readiness_grading",
                "production_blocker_grading",
                "final_audit_report",
            ],
            "status": "completed",
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat(),
            "duration_seconds": round(
                (
                    completed_at
                    - started_at
                ).total_seconds(),
                6,
            ),
            "discovery": discovery,
            "layer_mapping": layer_mapping,
            "dependency_mapping": dependency_mapping,
            "import_graph": import_graph,
            "runtime_graph": runtime_graph,
            "contract_discovery": contract_discovery,
            "fintech_capability": fintech_capability,
            "ai_capability": ai_capability,
            "production_readiness": production_readiness,
            "production_blockers": production_blockers,
            "final_report": final_report,
            "grading": {
                "status": "completed",
                "completed_grading_stages": [
                    "fintech_capability_grading",
                    "ai_capability_grading",
                    "production_readiness_grading",
                    "production_blocker_grading",
                    "final_audit_report",
                ],
                "pending_grading_stages": [],
                "production_readiness_status": "completed",
                "production_blocker_status": "completed",
                "deployment_approved": False,
                "live_trading_approved": False,
                "reason": (
                    "Capability, readiness, blocker grading, and final "
                    "remediation planning are complete. Deployment and "
                    "live trading remain unapproved."
                ),
            },
        }
