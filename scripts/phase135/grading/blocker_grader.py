#!/usr/bin/env python3

"""
Phase 135 Production Blocker Grader.

Consumes only evidence produced by earlier Phase 135 stages.

It does not:

- rescan the repository
- execute application code
- modify application code
- modify fintech, AI, or production-readiness scores
- approve deployment
- approve live trading

The grader classifies findings independently as:

1. CRITICAL_BLOCKER
   A condition that prevents safe production deployment or live trading.

2. HIGH_BLOCKER
   A serious production-readiness defect that must be resolved before release.

3. DEFERRED_INTEGRATION
   A deliberately postponed external connection or authorization workflow.

4. MATURITY_GAP
   Testing, observability, contracts, cleanup, or validation still required.

5. INFORMATIONAL
   Evidence that should be reviewed but is not independently blocking.

The grader also separates:

- paper-mode deployment eligibility
- authenticated broker integration eligibility
- live-trading eligibility

No eligibility result is an approval.
"""

from __future__ import annotations

from collections import Counter
from typing import Any


SEVERITY_ORDER = {
    "CRITICAL_BLOCKER": 0,
    "HIGH_BLOCKER": 1,
    "DEFERRED_INTEGRATION": 2,
    "MATURITY_GAP": 3,
    "INFORMATIONAL": 4,
}


DEFERRED_CHECK_IDS = {
    "broker_score",
    "auth_score",
    "fintech_auth_score",
    "credential_handling",
    "authentication_tests",
    "account_connectivity",
    "broker_runtime",
    "protected_api",
    "credential_or_token_handling",
    "auth_tests",
}


CRITICAL_CHECK_IDS = {
    "input_validation",
    "prompt_injection_or_input_validation",
    "tool_authorization",
    "ai_safety_score",
    "ai_safety_tests",
    "immutable_audit",
    "immutable_or_append_only",
}


HIGH_CHECK_IDS = {
    "multi_package_cycles",
    "dependency_cycles",
    "runtime_cycles",
    "runtime_reachability",
    "unresolved_dependencies",
    "route_contract_coverage",
    "routes_with_response_models",
    "duplicate_contract_names",
    "duplicate_contract_declarations",
    "active_source_ownership",
    "ambiguous_regions",
    "tool_score",
    "tool_registry",
    "tool_dispatch",
    "uncertainty_handling",
}


MATURITY_CHECK_IDS = {
    "test_files",
    "test_to_source_ratio",
    "fintech_test_checks",
    "ai_test_checks",
    "api_contract_coverage",
    "ai_logging",
    "ai_trace",
    "runtime_logging",
    "audit_logging_score",
    "audit_score",
    "fintech_gaps",
    "ai_gaps",
    "contract_parse_errors",
    "dependency_parse_errors",
    "runtime_parse_errors",
}


class ProductionBlockerGrader:
    """
    Classify production-readiness findings without changing prior grades.
    """

    def __init__(
        self,
        discovery: dict[str, Any],
        layer_mapping: dict[str, Any],
        dependency_mapping: dict[str, Any],
        import_graph: dict[str, Any],
        runtime_graph: dict[str, Any],
        contract_discovery: dict[str, Any],
        fintech_capability: dict[str, Any],
        ai_capability: dict[str, Any],
        production_readiness: dict[str, Any],
    ) -> None:
        self.discovery = discovery
        self.layer_mapping = layer_mapping
        self.dependency_mapping = dependency_mapping
        self.import_graph = import_graph
        self.runtime_graph = runtime_graph
        self.contract_discovery = contract_discovery
        self.fintech_capability = fintech_capability
        self.ai_capability = ai_capability
        self.production_readiness = production_readiness

        self.fintech_categories = {
            item["category_id"]: item
            for item in fintech_capability.get("categories", [])
        }

        self.ai_categories = {
            item["category_id"]: item
            for item in ai_capability.get("categories", [])
        }

        self.fintech_checks = self._build_check_index(
            fintech_capability
        )

        self.ai_checks = self._build_check_index(
            ai_capability
        )

        self.readiness_checks = self._build_check_index(
            production_readiness
        )

    def grade(self) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []

        findings.extend(
            self._classify_readiness_gaps()
        )

        findings.extend(
            self._generate_structural_findings()
        )

        findings.extend(
            self._generate_deferred_integration_findings()
        )

        findings.extend(
            self._generate_capability_findings()
        )

        findings = self._deduplicate_findings(findings)

        findings = sorted(
            findings,
            key=lambda item: (
                SEVERITY_ORDER[item["classification"]],
                -item["priority"],
                item["domain"],
                item["title"],
            ),
        )

        counts = Counter(
            item["classification"]
            for item in findings
        )

        blocking_findings = [
            item
            for item in findings
            if item["classification"]
            in {
                "CRITICAL_BLOCKER",
                "HIGH_BLOCKER",
            }
        ]

        critical_blockers = [
            item
            for item in findings
            if item["classification"] == "CRITICAL_BLOCKER"
        ]

        high_blockers = [
            item
            for item in findings
            if item["classification"] == "HIGH_BLOCKER"
        ]

        deferred_integrations = [
            item
            for item in findings
            if item["classification"] == "DEFERRED_INTEGRATION"
        ]

        maturity_gaps = [
            item
            for item in findings
            if item["classification"] == "MATURITY_GAP"
        ]

        informational = [
            item
            for item in findings
            if item["classification"] == "INFORMATIONAL"
        ]

        eligibility = self._build_eligibility(
            critical_blockers=critical_blockers,
            high_blockers=high_blockers,
            deferred_integrations=deferred_integrations,
        )

        remediation_order = self._build_remediation_order(
            findings
        )

        final_status = self._overall_status(
            critical_count=len(critical_blockers),
            high_count=len(high_blockers),
        )

        return {
            "grading_mode": "evidence_based_blocker_classification",
            "application_executed": False,
            "repository_rescanned": False,
            "architecture_assumed": False,
            "fintech_score_modified": False,
            "ai_score_modified": False,
            "production_readiness_score_modified": False,
            "deployment_approved": False,
            "live_trading_approved": False,
            "summary": {
                "finding_count": len(findings),
                "blocking_finding_count": len(blocking_findings),
                "critical_blockers": len(critical_blockers),
                "high_blockers": len(high_blockers),
                "deferred_integrations": len(deferred_integrations),
                "maturity_gaps": len(maturity_gaps),
                "informational_findings": len(informational),
                "overall_status": final_status,
            },
            "classification_counts": {
                classification: counts.get(classification, 0)
                for classification in SEVERITY_ORDER
            },
            "findings": findings,
            "critical_blockers": critical_blockers,
            "high_blockers": high_blockers,
            "deferred_integrations": deferred_integrations,
            "maturity_gaps": maturity_gaps,
            "informational_findings": informational,
            "eligibility": eligibility,
            "remediation_order": remediation_order,
            "scoring_contract": {
                "classification_order": [
                    "CRITICAL_BLOCKER",
                    "HIGH_BLOCKER",
                    "DEFERRED_INTEGRATION",
                    "MATURITY_GAP",
                    "INFORMATIONAL",
                ],
                "critical_blocker_definition": (
                    "A condition preventing safe production deployment "
                    "or live-trading enablement."
                ),
                "high_blocker_definition": (
                    "A serious architecture, runtime, contract, dependency, "
                    "or integrity issue requiring remediation before release."
                ),
                "deferred_integration_definition": (
                    "A deliberately postponed external authorization, "
                    "credential, broker, or provider integration."
                ),
                "maturity_gap_definition": (
                    "Testing, observability, documentation, coverage, "
                    "cleanup, or validation work still required."
                ),
                "eligibility_is_not_approval": True,
            },
            "limitations": [
                (
                    "Blocker classifications are based on static evidence "
                    "and prior Phase 135 grading results."
                ),
                (
                    "The grader cannot prove that a missing static signal "
                    "means the underlying capability does not exist."
                ),
                (
                    "Deferred-integration classification does not prove that "
                    "the surrounding architecture is correctly wired."
                ),
                (
                    "No deployment, broker, database, model-provider, "
                    "authentication, or live-trading workflow was executed."
                ),
                (
                    "The blocker report does not authorize production use "
                    "or live trading."
                ),
            ],
        }

    def _classify_readiness_gaps(
        self,
    ) -> list[dict[str, Any]]:
        findings = []

        for gap in self.production_readiness.get(
            "readiness_gaps",
            [],
        ):
            check_id = str(
                gap.get("check_id", "")
            )

            category_id = str(
                gap.get("category_id", "")
            )

            classification, reason = self._classify_gap(
                check_id=check_id,
                category_id=category_id,
                title=str(gap.get("check", "")),
            )

            findings.append(
                self._finding(
                    finding_id=(
                        f"readiness.{category_id}.{check_id}"
                    ),
                    classification=classification,
                    domain=str(
                        gap.get(
                            "category",
                            category_id,
                        )
                    ),
                    title=str(
                        gap.get(
                            "check",
                            check_id,
                        )
                    ),
                    description=reason,
                    evidence={
                        "source": "production_readiness",
                        "observed": gap.get("observed"),
                        "requirement": gap.get("requirement"),
                        "points_available": gap.get(
                            "points_available"
                        ),
                    },
                    remediation=self._remediation_for_check(
                        check_id
                    ),
                    priority=self._priority_for_classification(
                        classification
                    ),
                    blocks_paper_mode=self._blocks_paper_mode(
                        check_id,
                        classification,
                    ),
                    blocks_broker_integration=self._blocks_broker(
                        check_id,
                        classification,
                    ),
                    blocks_live_trading=self._blocks_live_trading(
                        check_id,
                        classification,
                    ),
                )
            )

        return findings

    def _generate_structural_findings(
        self,
    ) -> list[dict[str, Any]]:
        findings = []

        dependency_summary = self.dependency_mapping.get(
            "summary",
            {},
        )

        unresolved = int(
            dependency_summary.get(
                "unresolved_dependencies",
                0,
            )
        )

        if unresolved > 0:
            findings.append(
                self._finding(
                    finding_id="structure.unresolved_dependencies",
                    classification="HIGH_BLOCKER",
                    domain="Dependency Health",
                    title="Unresolved static dependencies",
                    description=(
                        f"{unresolved} static dependency references "
                        "could not be resolved."
                    ),
                    evidence={
                        "count": unresolved,
                        "groups": self.import_graph.get(
                            "unresolved_groups",
                            [],
                        ),
                    },
                    remediation=(
                        "Classify unresolved references as valid aliases, "
                        "optional imports, archived paths, or broken imports; "
                        "repair all active broken imports."
                    ),
                    priority=90,
                    blocks_paper_mode=True,
                    blocks_broker_integration=True,
                    blocks_live_trading=True,
                )
            )

        file_cycles = int(
            dependency_summary.get(
                "dependency_cycles",
                0,
            )
        )

        if file_cycles > 0:
            findings.append(
                self._finding(
                    finding_id="structure.file_dependency_cycles",
                    classification="HIGH_BLOCKER",
                    domain="Architecture Integrity",
                    title="File-level dependency cycle",
                    description=(
                        f"{file_cycles} file-level dependency cycle "
                        "component was discovered."
                    ),
                    evidence=self.dependency_mapping.get(
                        "cycles",
                        [],
                    ),
                    remediation=(
                        "Break cyclic ownership by extracting shared "
                        "contracts, interfaces, events, or persistence "
                        "boundaries into an acyclic owner."
                    ),
                    priority=95,
                    blocks_paper_mode=True,
                    blocks_broker_integration=True,
                    blocks_live_trading=True,
                )
            )

        package_cycles = [
            cycle
            for cycle in (
                self.import_graph
                .get("package_graph", {})
                .get("cycles", [])
            )
            if int(cycle.get("node_count", 0)) > 1
        ]

        if package_cycles:
            findings.append(
                self._finding(
                    finding_id="structure.cross_package_cycles",
                    classification="HIGH_BLOCKER",
                    domain="Architecture Integrity",
                    title="Cross-package dependency cycles",
                    description=(
                        f"{len(package_cycles)} multi-package cycle "
                        "components were discovered."
                    ),
                    evidence=package_cycles,
                    remediation=(
                        "Resolve package cycles by enforcing one-way "
                        "ownership and replacing reverse imports with "
                        "contracts, events, or facade calls."
                    ),
                    priority=98,
                    blocks_paper_mode=True,
                    blocks_broker_integration=True,
                    blocks_live_trading=True,
                )
            )

        runtime_summary = self.runtime_graph.get(
            "summary",
            {},
        )

        reachable = int(
            runtime_summary.get(
                "reachable_files",
                0,
            )
        )

        unreachable = int(
            runtime_summary.get(
                "unreachable_active_files",
                0,
            )
        )

        if unreachable > reachable:
            findings.append(
                self._finding(
                    finding_id="runtime.unreachable_active_code",
                    classification="HIGH_BLOCKER",
                    domain="Runtime Readiness",
                    title="Large unreachable active-code surface",
                    description=(
                        f"{unreachable} active files were not statically "
                        f"reachable while only {reachable} were reachable."
                    ),
                    evidence={
                        "reachable_files": reachable,
                        "unreachable_active_files": unreachable,
                    },
                    remediation=(
                        "Classify every unreachable active file as runtime "
                        "entrypoint, dynamically loaded module, dormant feature, "
                        "tooling, test support, or dead code."
                    ),
                    priority=88,
                    blocks_paper_mode=True,
                    blocks_broker_integration=False,
                    blocks_live_trading=True,
                )
            )

        return findings

    def _generate_deferred_integration_findings(
        self,
    ) -> list[dict[str, Any]]:
        findings = []

        broker = self.fintech_categories.get(
            "broker_integration",
            {},
        )

        auth = self.fintech_categories.get(
            "authentication_identity",
            {},
        )

        if float(broker.get("percentage", 0.0)) < 80.0:
            findings.append(
                self._finding(
                    finding_id="deferred.broker_integration",
                    classification="DEFERRED_INTEGRATION",
                    domain="Broker Integration",
                    title="Authenticated broker connectivity deferred",
                    description=(
                        "Broker account authorization and integration "
                        "remain below the production threshold."
                    ),
                    evidence={
                        "category_score": broker.get("percentage", 0.0),
                        "missing": broker.get("missing", []),
                    },
                    remediation=(
                        "Complete the SnapTrade authorization lifecycle, "
                        "secure connection storage, reconnect state, account "
                        "selection, and broker integration tests."
                    ),
                    priority=75,
                    blocks_paper_mode=False,
                    blocks_broker_integration=True,
                    blocks_live_trading=True,
                )
            )

        if float(auth.get("percentage", 0.0)) < 80.0:
            findings.append(
                self._finding(
                    finding_id="deferred.authentication_identity",
                    classification="DEFERRED_INTEGRATION",
                    domain="Authentication and Identity",
                    title="Authentication and credential lifecycle deferred",
                    description=(
                        "Authentication, credential handling, and related "
                        "tests remain below the production threshold."
                    ),
                    evidence={
                        "category_score": auth.get("percentage", 0.0),
                        "missing": auth.get("missing", []),
                    },
                    remediation=(
                        "Implement the identity boundary, credential storage, "
                        "session lifecycle, permissions, expiry handling, and "
                        "authentication integration tests."
                    ),
                    priority=80,
                    blocks_paper_mode=True,
                    blocks_broker_integration=True,
                    blocks_live_trading=True,
                )
            )

        return findings

    def _generate_capability_findings(
        self,
    ) -> list[dict[str, Any]]:
        findings = []

        tool_category = self.ai_categories.get(
            "tool_invocation",
            {},
        )

        if float(
            tool_category.get("percentage", 0.0)
        ) < 80.0:
            findings.append(
                self._finding(
                    finding_id="ai.tool_invocation_incomplete",
                    classification="CRITICAL_BLOCKER",
                    domain="AI Safety and Runtime",
                    title="AI tool invocation boundary incomplete",
                    description=(
                        "The tool registry, dispatcher, authorization boundary, "
                        "or tests are not sufficiently evidenced."
                    ),
                    evidence={
                        "category_score": tool_category.get(
                            "percentage",
                            0.0,
                        ),
                        "missing": tool_category.get(
                            "missing",
                            [],
                        ),
                    },
                    remediation=(
                        "Create an explicit allowlisted tool registry, "
                        "authorization policy, typed invocation contract, "
                        "dispatcher, execution audit record, timeout handling, "
                        "and deny-by-default tests."
                    ),
                    priority=100,
                    blocks_paper_mode=False,
                    blocks_broker_integration=False,
                    blocks_live_trading=True,
                )
            )

        ai_safety = self.ai_categories.get(
            "ai_safety_governance",
            {},
        )

        if float(
            ai_safety.get("percentage", 0.0)
        ) < 80.0:
            findings.append(
                self._finding(
                    finding_id="ai.safety_governance_incomplete",
                    classification="CRITICAL_BLOCKER",
                    domain="AI Safety and Risk Governance",
                    title="AI safety governance below production threshold",
                    description=(
                        "Input validation, AI safety tests, or governance "
                        "controls remain incomplete."
                    ),
                    evidence={
                        "category_score": ai_safety.get(
                            "percentage",
                            0.0,
                        ),
                        "missing": ai_safety.get(
                            "missing",
                            [],
                        ),
                    },
                    remediation=(
                        "Implement validated AI input contracts, unsafe-input "
                        "handling, prompt-injection resistance, risk integration, "
                        "action restrictions, and adversarial safety tests."
                    ),
                    priority=100,
                    blocks_paper_mode=False,
                    blocks_broker_integration=False,
                    blocks_live_trading=True,
                )
            )

        coverage = float(
            self.contract_discovery
            .get("route_contract_coverage", {})
            .get(
                "explicit_contract_coverage_percent",
                0.0,
            )
        )

        if coverage < 80.0:
            findings.append(
                self._finding(
                    finding_id="contracts.route_coverage",
                    classification="HIGH_BLOCKER",
                    domain="Contract Readiness",
                    title="API contract coverage below production threshold",
                    description=(
                        f"Explicit route-contract coverage is {coverage}%."
                    ),
                    evidence=self.contract_discovery.get(
                        "route_contract_coverage",
                        {},
                    ),
                    remediation=(
                        "Add explicit request and response DTOs to active API "
                        "routes and verify frontend/backend compatibility."
                    ),
                    priority=92,
                    blocks_paper_mode=True,
                    blocks_broker_integration=True,
                    blocks_live_trading=True,
                )
            )

        test_files = int(
            self.discovery
            .get("summary", {})
            .get("test_files", 0)
        )

        source_files = int(
            self.discovery
            .get("summary", {})
            .get("source_files", 0)
        )

        if source_files and (
            test_files / source_files
        ) < 0.10:
            findings.append(
                self._finding(
                    finding_id="testing.insufficient_coverage",
                    classification="MATURITY_GAP",
                    domain="Testing Readiness",
                    title="Insufficient L7 test evidence",
                    description=(
                        f"{test_files} discovered test files cover "
                        f"{source_files} source files."
                    ),
                    evidence={
                        "test_files": test_files,
                        "source_files": source_files,
                        "ratio": round(
                            test_files / source_files,
                            6,
                        ),
                    },
                    remediation=(
                        "Add contract, unit, integration, runtime, safety, "
                        "database, broker, risk, paper-trading, frontend, and "
                        "end-to-end tests."
                    ),
                    priority=85,
                    blocks_paper_mode=True,
                    blocks_broker_integration=True,
                    blocks_live_trading=True,
                )
            )

        return findings

    def _classify_gap(
        self,
        check_id: str,
        category_id: str,
        title: str,
    ) -> tuple[str, str]:
        normalized_title = title.lower()

        if check_id in DEFERRED_CHECK_IDS:
            return (
                "DEFERRED_INTEGRATION",
                (
                    "This finding concerns a deliberately postponed "
                    "authentication, credential, or broker integration."
                ),
            )

        if check_id in CRITICAL_CHECK_IDS:
            return (
                "CRITICAL_BLOCKER",
                (
                    "This missing control can directly affect safety, "
                    "authorization, action governance, or audit integrity."
                ),
            )

        if check_id in HIGH_CHECK_IDS:
            return (
                "HIGH_BLOCKER",
                (
                    "This finding affects architecture, runtime integrity, "
                    "dependency health, API contracts, or active execution."
                ),
            )

        if check_id in MATURITY_CHECK_IDS:
            return (
                "MATURITY_GAP",
                (
                    "This finding represents incomplete verification, "
                    "observability, coverage, or operational maturity."
                ),
            )

        if category_id in {
            "testing_readiness",
            "observability_auditability",
        }:
            return (
                "MATURITY_GAP",
                (
                    "This finding is primarily a verification or "
                    "operational-maturity concern."
                ),
            )

        if category_id in {
            "security_identity",
            "ai_production_readiness",
        }:
            if any(
                word in normalized_title
                for word in {
                    "auth",
                    "credential",
                    "broker",
                }
            ):
                return (
                    "DEFERRED_INTEGRATION",
                    (
                        "The finding belongs to the intentionally deferred "
                        "identity or broker integration boundary."
                    ),
                )

            return (
                "CRITICAL_BLOCKER",
                (
                    "The finding affects security, authorization, AI safety, "
                    "or governed production action."
                ),
            )

        if category_id in {
            "architecture_integrity",
            "dependency_health",
            "runtime_readiness",
            "contract_readiness",
        }:
            return (
                "HIGH_BLOCKER",
                (
                    "The finding affects structural or runtime correctness."
                ),
            )

        return (
            "MATURITY_GAP",
            (
                "The finding requires remediation before a production "
                "release candidate can be accepted."
            ),
        )

    @staticmethod
    def _remediation_for_check(
        check_id: str,
    ) -> str:
        remediation = {
            "ambiguous_regions": (
                "Assign every source-bearing directory to an explicit owner."
            ),
            "multi_package_cycles": (
                "Break cross-package cycles using contracts, facades, or events."
            ),
            "dependency_cycles": (
                "Break file-level cycles and enforce acyclic import direction."
            ),
            "duplicate_contract_names": (
                "Consolidate, version, or explicitly namespace duplicate contracts."
            ),
            "unresolved_dependencies": (
                "Resolve active imports and classify valid aliases or optional imports."
            ),
            "runtime_reachability": (
                "Connect intended runtime modules or classify dormant/dead code."
            ),
            "runtime_cycles": (
                "Break runtime import cycles before production startup."
            ),
            "route_contract_coverage": (
                "Add explicit request and response DTOs to active routes."
            ),
            "routes_with_response_models": (
                "Declare explicit response models or return contracts."
            ),
            "test_files": (
                "Add production-grade L7 unit and integration tests."
            ),
            "test_to_source_ratio": (
                "Increase verified test coverage across active runtime code."
            ),
            "fintech_test_checks": (
                "Add tests for market, portfolio, broker, risk, and ledger paths."
            ),
            "ai_test_checks": (
                "Add tests for providers, prompts, tools, memory, safety, and AI runtime."
            ),
            "credential_handling": (
                "Implement secure credential and token lifecycle management."
            ),
            "authentication_tests": (
                "Add authentication, authorization, expiry, and denial tests."
            ),
            "input_validation": (
                "Validate and sanitize external and AI-facing inputs."
            ),
            "immutable_audit": (
                "Implement append-only or immutable execution audit records."
            ),
            "tool_score": (
                "Complete the allowlisted tool registry, dispatcher, and authorization."
            ),
            "ai_safety_score": (
                "Complete AI safety controls and adversarial tests."
            ),
            "ai_gaps": (
                "Close unresolved AI capability gaps before production release."
            ),
            "fintech_gaps": (
                "Close unresolved fintech capability gaps before production release."
            ),
        }

        return remediation.get(
            check_id,
            (
                "Implement the missing control and add deterministic "
                "verification evidence."
            ),
        )

    @staticmethod
    def _priority_for_classification(
        classification: str,
    ) -> int:
        return {
            "CRITICAL_BLOCKER": 100,
            "HIGH_BLOCKER": 90,
            "DEFERRED_INTEGRATION": 75,
            "MATURITY_GAP": 60,
            "INFORMATIONAL": 25,
        }[classification]

    @staticmethod
    def _blocks_paper_mode(
        check_id: str,
        classification: str,
    ) -> bool:
        if check_id in {
            "broker_score",
            "account_connectivity",
            "broker_runtime",
        }:
            return False

        if classification == "CRITICAL_BLOCKER":
            return check_id not in {
                "tool_authorization",
                "tool_score",
            }

        return check_id in {
            "dependency_cycles",
            "multi_package_cycles",
            "runtime_cycles",
            "runtime_reachability",
            "unresolved_dependencies",
            "route_contract_coverage",
            "test_files",
            "test_to_source_ratio",
            "credential_handling",
            "authentication_tests",
        }

    @staticmethod
    def _blocks_broker(
        check_id: str,
        classification: str,
    ) -> bool:
        if classification in {
            "CRITICAL_BLOCKER",
            "HIGH_BLOCKER",
        }:
            return True

        return check_id in DEFERRED_CHECK_IDS

    @staticmethod
    def _blocks_live_trading(
        check_id: str,
        classification: str,
    ) -> bool:
        return classification in {
            "CRITICAL_BLOCKER",
            "HIGH_BLOCKER",
            "DEFERRED_INTEGRATION",
        } or check_id in {
            "test_files",
            "test_to_source_ratio",
            "fintech_test_checks",
            "ai_test_checks",
            "immutable_audit",
        }

    def _build_eligibility(
        self,
        critical_blockers: list[dict[str, Any]],
        high_blockers: list[dict[str, Any]],
        deferred_integrations: list[dict[str, Any]],
    ) -> dict[str, Any]:
        paper_blockers = [
            item
            for item in (
                critical_blockers
                + high_blockers
                + deferred_integrations
            )
            if item["blocks_paper_mode"]
        ]

        broker_blockers = [
            item
            for item in (
                critical_blockers
                + high_blockers
                + deferred_integrations
            )
            if item["blocks_broker_integration"]
        ]

        live_blockers = [
            item
            for item in (
                critical_blockers
                + high_blockers
                + deferred_integrations
            )
            if item["blocks_live_trading"]
        ]

        return {
            "paper_mode": {
                "eligible": len(paper_blockers) == 0,
                "approved": False,
                "blocking_findings": [
                    item["finding_id"]
                    for item in paper_blockers
                ],
            },
            "authenticated_broker_integration": {
                "eligible": len(broker_blockers) == 0,
                "approved": False,
                "blocking_findings": [
                    item["finding_id"]
                    for item in broker_blockers
                ],
            },
            "live_trading": {
                "eligible": len(live_blockers) == 0,
                "approved": False,
                "blocking_findings": [
                    item["finding_id"]
                    for item in live_blockers
                ],
            },
        }

    @staticmethod
    def _build_remediation_order(
        findings: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        ordered = []

        for position, finding in enumerate(
            findings,
            start=1,
        ):
            ordered.append(
                {
                    "order": position,
                    "finding_id": finding["finding_id"],
                    "classification": finding["classification"],
                    "domain": finding["domain"],
                    "title": finding["title"],
                    "remediation": finding["remediation"],
                }
            )

        return ordered

    @staticmethod
    def _overall_status(
        critical_count: int,
        high_count: int,
    ) -> str:
        if critical_count > 0:
            return "BLOCKED_CRITICAL"

        if high_count > 0:
            return "BLOCKED_HIGH"

        return "NO_BLOCKING_FINDINGS"

    @staticmethod
    def _finding(
        finding_id: str,
        classification: str,
        domain: str,
        title: str,
        description: str,
        evidence: Any,
        remediation: str,
        priority: int,
        blocks_paper_mode: bool,
        blocks_broker_integration: bool,
        blocks_live_trading: bool,
    ) -> dict[str, Any]:
        return {
            "finding_id": finding_id,
            "classification": classification,
            "domain": domain,
            "title": title,
            "description": description,
            "evidence": evidence,
            "remediation": remediation,
            "priority": priority,
            "blocks_paper_mode": blocks_paper_mode,
            "blocks_broker_integration": blocks_broker_integration,
            "blocks_live_trading": blocks_live_trading,
        }

    @staticmethod
    def _build_check_index(
        grading_result: dict[str, Any],
    ) -> dict[str, dict[str, Any]]:
        index = {}

        for category in grading_result.get(
            "categories",
            [],
        ):
            for check in category.get(
                "checks",
                [],
            ):
                check_id = check.get("check_id")

                if check_id:
                    index[str(check_id)] = check

        return index

    @staticmethod
    def _deduplicate_findings(
        findings: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        deduplicated = {}

        for finding in findings:
            finding_id = finding["finding_id"]

            existing = deduplicated.get(finding_id)

            if existing is None:
                deduplicated[finding_id] = finding
                continue

            existing_order = SEVERITY_ORDER[
                existing["classification"]
            ]

            current_order = SEVERITY_ORDER[
                finding["classification"]
            ]

            if current_order < existing_order:
                deduplicated[finding_id] = finding
                continue

            existing["blocks_paper_mode"] = (
                existing["blocks_paper_mode"]
                or finding["blocks_paper_mode"]
            )

            existing["blocks_broker_integration"] = (
                existing["blocks_broker_integration"]
                or finding["blocks_broker_integration"]
            )

            existing["blocks_live_trading"] = (
                existing["blocks_live_trading"]
                or finding["blocks_live_trading"]
            )

            existing["priority"] = max(
                existing["priority"],
                finding["priority"],
            )

        return list(deduplicated.values())
