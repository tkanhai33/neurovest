#!/usr/bin/env python3

"""
Phase 135 Final Audit Report and Prioritized Remediation Plan.

Consumes completed Stage 1-10 evidence and produces:

- executive summary
- normalized root-cause workstreams
- duplicate-finding consolidation
- paper-mode remediation path
- authenticated broker integration path
- live-trading remediation path
- dependency-aware implementation order
- acceptance criteria
- completion gates
- concise JSON report
- human-readable text report

This stage does not:

- rescan the repository
- execute application code
- modify application code
- create new blocker evidence
- change any prior score
- approve deployment
- approve live trading
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


ROOT_CAUSE_RULES: list[dict[str, Any]] = [
    {
        "id": "ai_tool_boundary",
        "title": "Complete AI Tool Invocation Boundary",
        "classification": "CRITICAL_BLOCKER",
        "finding_keywords": {
            "tool invocation",
            "tool registry",
            "tool dispatch",
            "tool authorization",
        },
        "dependencies": [
            "runtime_import_integrity",
            "api_contracts",
        ],
        "acceptance_criteria": [
            "A single allowlisted tool registry exists.",
            "Every tool uses a typed request and result contract.",
            "Unknown tools are denied by default.",
            "Authorization is checked before dispatch.",
            "Execution has timeout and failure handling.",
            "Every invocation produces an audit record.",
            "Unit, denial, timeout, and integration tests pass.",
        ],
    },
    {
        "id": "ai_input_safety",
        "title": "Complete AI Input Validation and Safety Governance",
        "classification": "CRITICAL_BLOCKER",
        "finding_keywords": {
            "ai safety",
            "prompt or input validation",
            "safety governance",
        },
        "dependencies": [
            "api_contracts",
            "immutable_audit",
        ],
        "acceptance_criteria": [
            "All AI-facing inputs use validated contracts.",
            "Malformed, oversized, and unsupported input is rejected.",
            "Prompt-injection and unsafe-action tests exist.",
            "AI outputs cannot bypass risk or execution policies.",
            "Unsafe or uncertain requests produce controlled denials.",
            "Safety decisions are written to the audit ledger.",
        ],
    },
    {
        "id": "confidence_uncertainty",
        "title": "Complete Confidence and Uncertainty Handling",
        "classification": "CRITICAL_BLOCKER",
        "finding_keywords": {
            "confidence and explainability",
            "overall ai capability",
            "uncertainty",
        },
        "dependencies": [
            "ai_input_safety",
        ],
        "acceptance_criteria": [
            "AI decisions expose a normalized confidence value.",
            "Confidence thresholds are centrally configured.",
            "Low-confidence outputs abstain or request more evidence.",
            "Explanations include evidence and uncertainty.",
            "Confidence and abstention tests pass.",
        ],
    },
    {
        "id": "immutable_audit",
        "title": "Implement Immutable Execution and Decision Audit Records",
        "classification": "CRITICAL_BLOCKER",
        "finding_keywords": {
            "append-only",
            "immutable audit",
            "audit evidence",
        },
        "dependencies": [
            "persistence_integrity",
        ],
        "acceptance_criteria": [
            "Execution and decision records are append-only.",
            "Records include timestamp, actor, mode, request, decision, and result.",
            "Audit records cannot be updated through normal application paths.",
            "Failures and denied actions are recorded.",
            "Integrity and replay-verification tests pass.",
        ],
    },
    {
        "id": "runtime_import_integrity",
        "title": "Resolve Active Imports and Dependency Cycles",
        "classification": "HIGH_BLOCKER",
        "finding_keywords": {
            "unresolved static dependencies",
            "controlled unresolved dependencies",
            "dependency cycle",
            "cross-package dependency cycles",
            "file-level dependency cycle",
            "runtime dependency cycles",
        },
        "dependencies": [],
        "acceptance_criteria": [
            "Every active unresolved import is classified.",
            "Broken active imports are repaired.",
            "Valid aliases and optional imports are documented.",
            "No active multi-package cycle remains.",
            "No active file-level cycle remains.",
            "Architecture and import-graph verification passes.",
        ],
    },
    {
        "id": "runtime_reachability",
        "title": "Classify and Normalize Runtime Reachability",
        "classification": "HIGH_BLOCKER",
        "finding_keywords": {
            "runtime reachability",
            "unreachable active",
        },
        "dependencies": [
            "runtime_import_integrity",
        ],
        "acceptance_criteria": [
            "Every unreachable active file is classified.",
            "Runtime modules are connected to a valid entrypoint.",
            "Dormant features are explicitly marked.",
            "Tooling and generated files are excluded from runtime ownership.",
            "Dead code is removed or quarantined.",
            "Reachability report contains no unexplained active modules.",
        ],
    },
    {
        "id": "api_contracts",
        "title": "Formalize Active API Request and Response Contracts",
        "classification": "HIGH_BLOCKER",
        "finding_keywords": {
            "api contract coverage",
            "explicit route contract coverage",
            "explicit response models",
            "duplicate contract",
        },
        "dependencies": [
            "runtime_import_integrity",
        ],
        "acceptance_criteria": [
            "Every active API route has an explicit request contract where applicable.",
            "Every active API route has an explicit response contract.",
            "Frontend and backend route contracts are compatible.",
            "Duplicate contracts are consolidated, versioned, or namespaced.",
            "Route-contract coverage reaches at least 80 percent.",
            "Contract tests pass.",
        ],
    },
    {
        "id": "source_ownership",
        "title": "Assign Explicit Ownership to Active Source Regions",
        "classification": "HIGH_BLOCKER",
        "finding_keywords": {
            "ambiguous source ownership",
        },
        "dependencies": [
            "runtime_import_integrity",
        ],
        "acceptance_criteria": [
            "Every active source directory has one explicit architectural owner.",
            "Application, tooling, archive, generated, and test regions are separated.",
            "No production package imports audit tooling.",
            "Ownership verification passes.",
        ],
    },
    {
        "id": "l7_verification",
        "title": "Build the L7 Verification Baseline",
        "classification": "MATURITY_GAP",
        "finding_keywords": {
            "test evidence",
            "test-file inventory",
            "test-to-source ratio",
            "test-capability checks",
            "testing",
        },
        "dependencies": [
            "runtime_import_integrity",
            "runtime_reachability",
            "api_contracts",
        ],
        "acceptance_criteria": [
            "Core unit tests exist for market, portfolio, strategy, risk, and persistence.",
            "Integration tests cover API, database, paper trading, chat, and runtime paths.",
            "Safety tests cover denial and emergency conditions.",
            "Contract tests cover frontend/backend DTO compatibility.",
            "End-to-end paper-mode smoke tests pass.",
            "All critical workstreams have deterministic regression tests.",
        ],
    },
    {
        "id": "auth_identity",
        "title": "Complete Authentication and Credential Lifecycle",
        "classification": "DEFERRED_INTEGRATION",
        "finding_keywords": {
            "authentication",
            "credential lifecycle",
            "credential or token handling",
            "authentication tests",
        },
        "dependencies": [
            "api_contracts",
            "immutable_audit",
            "l7_verification",
        ],
        "acceptance_criteria": [
            "Identity and permission boundaries are implemented.",
            "Credentials and tokens are stored securely.",
            "Expiry and reconnect states are handled.",
            "Unauthorized calls are denied.",
            "Authentication and authorization tests pass.",
            "Credential events are audited.",
        ],
    },
    {
        "id": "broker_integration",
        "title": "Complete Authenticated SnapTrade Integration",
        "classification": "DEFERRED_INTEGRATION",
        "finding_keywords": {
            "broker connectivity",
            "broker integration capability",
            "broker integration",
        },
        "dependencies": [
            "auth_identity",
            "runtime_import_integrity",
            "api_contracts",
            "l7_verification",
        ],
        "acceptance_criteria": [
            "SnapTrade authorization completes through the identity boundary.",
            "Connection identifiers are stored securely.",
            "Account discovery and selection work.",
            "Expired or revoked connections produce controlled reconnect state.",
            "Broker DTOs remain isolated behind the broker facade.",
            "Broker integration tests pass without enabling live trading.",
        ],
    },
    {
        "id": "persistence_integrity",
        "title": "Validate Persistence and Transaction Integrity",
        "classification": "MATURITY_GAP",
        "finding_keywords": {
            "audit and journal capability",
            "persistence",
            "journal capability",
        },
        "dependencies": [
            "runtime_import_integrity",
        ],
        "acceptance_criteria": [
            "Database initialization and migrations are deterministic.",
            "Repository boundaries are explicit.",
            "Transaction rollback and failure behavior is tested.",
            "Paper-trade, portfolio, conversation, and audit persistence tests pass.",
        ],
    },
    {
        "id": "observability",
        "title": "Complete Runtime and AI Observability",
        "classification": "MATURITY_GAP",
        "finding_keywords": {
            "ai-specific logging",
            "audit and logging capability",
            "runtime logging",
            "observability",
        },
        "dependencies": [
            "immutable_audit",
            "runtime_reachability",
        ],
        "acceptance_criteria": [
            "Runtime requests have correlation identifiers.",
            "AI calls record provider, model, duration, status, and token usage when available.",
            "Errors preserve stack and boundary context.",
            "Health and diagnostic endpoints expose safe operational status.",
            "Logs do not expose credentials or private tokens.",
        ],
    },
    {
        "id": "fintech_gap_closure",
        "title": "Close Remaining Fintech Capability Gaps",
        "classification": "MATURITY_GAP",
        "finding_keywords": {
            "controlled fintech capability gaps",
        },
        "dependencies": [
            "l7_verification",
            "auth_identity",
            "broker_integration",
            "immutable_audit",
        ],
        "acceptance_criteria": [
            "Fintech capability score reaches the configured release threshold.",
            "Market, portfolio, broker, risk, research, and audit gaps are closed or waived.",
            "All waivers include owner, reason, risk, and expiry.",
        ],
    },
    {
        "id": "ai_gap_closure",
        "title": "Close Remaining AI Capability Gaps",
        "classification": "MATURITY_GAP",
        "finding_keywords": {
            "controlled ai capability gaps",
        },
        "dependencies": [
            "ai_tool_boundary",
            "ai_input_safety",
            "confidence_uncertainty",
            "l7_verification",
        ],
        "acceptance_criteria": [
            "AI capability score reaches the configured release threshold.",
            "Memory, tools, safety, explainability, and test gaps are closed or waived.",
            "All waivers include owner, reason, risk, and expiry.",
        ],
    },
]


class FinalAuditReportBuilder:
    """
    Convert Stage 10 findings into a dependency-aware remediation roadmap.
    """

    def __init__(
        self,
        audit: dict[str, Any],
    ) -> None:
        self.audit = audit
        self.blockers = audit.get(
            "production_blockers",
            {},
        )
        self.readiness = audit.get(
            "production_readiness",
            {},
        )
        self.fintech = audit.get(
            "fintech_capability",
            {},
        )
        self.ai = audit.get(
            "ai_capability",
            {},
        )

    def build(self) -> dict[str, Any]:
        raw_findings = list(
            self.blockers.get("findings", [])
        )

        workstreams = self._build_workstreams(
            raw_findings
        )

        workstreams = self._dependency_order(
            workstreams
        )

        paper_path = self._mode_path(
            workstreams,
            mode_field="blocks_paper_mode",
        )

        broker_path = self._mode_path(
            workstreams,
            mode_field="blocks_broker_integration",
        )

        live_path = self._mode_path(
            workstreams,
            mode_field="blocks_live_trading",
        )

        orphan_findings = self._orphan_findings(
            raw_findings,
            workstreams,
        )

        executive = self._executive_summary(
            workstreams=workstreams,
            raw_findings=raw_findings,
            orphan_findings=orphan_findings,
        )

        release_gates = self._release_gates(
            workstreams
        )

        return {
            "report_type": (
                "final_audit_and_prioritized_remediation_plan"
            ),
            "source_phase": 135,
            "application_executed": False,
            "repository_rescanned": False,
            "application_modified": False,
            "prior_scores_modified": False,
            "new_findings_created": False,
            "deployment_approved": False,
            "live_trading_approved": False,
            "executive_summary": executive,
            "score_summary": {
                "fintech_capability": self.fintech.get(
                    "summary",
                    {},
                ),
                "ai_capability": self.ai.get(
                    "summary",
                    {},
                ),
                "production_readiness": self.readiness.get(
                    "summary",
                    {},
                ),
                "production_blockers": self.blockers.get(
                    "summary",
                    {},
                ),
            },
            "raw_finding_count": len(raw_findings),
            "root_workstream_count": len(workstreams),
            "duplicate_reduction": (
                len(raw_findings)
                - len(workstreams)
            ),
            "root_workstreams": workstreams,
            "paper_mode_path": paper_path,
            "authenticated_broker_path": broker_path,
            "live_trading_path": live_path,
            "orphan_findings": orphan_findings,
            "release_gates": release_gates,
            "final_status": {
                "paper_mode": self._mode_status(
                    paper_path
                ),
                "authenticated_broker": self._mode_status(
                    broker_path
                ),
                "live_trading": self._mode_status(
                    live_path
                ),
                "deployment_approved": False,
                "live_trading_approved": False,
            },
            "limitations": [
                (
                    "This report normalizes existing findings and does not "
                    "create new repository evidence."
                ),
                (
                    "Acceptance criteria require later implementation and "
                    "runtime verification."
                ),
                (
                    "No mode is approved by this report."
                ),
            ],
        }

    def render_text(
        self,
        report: dict[str, Any],
    ) -> str:
        executive = report["executive_summary"]
        scores = report["score_summary"]

        lines: list[str] = []

        lines.append("=" * 80)
        lines.append("PHASE 135")
        lines.append("FINAL AUDIT REPORT AND PRIORITIZED REMEDIATION PLAN")
        lines.append("=" * 80)
        lines.append("")
        lines.append("EXECUTIVE SUMMARY")
        lines.append(
            f"Raw findings:              "
            f"{report['raw_finding_count']}"
        )
        lines.append(
            f"Root workstreams:          "
            f"{report['root_workstream_count']}"
        )
        lines.append(
            f"Duplicate findings merged: "
            f"{report['duplicate_reduction']}"
        )
        lines.append(
            f"Overall blocker status:    "
            f"{executive['blocker_status']}"
        )
        lines.append("")
        lines.append("SCORES")
        lines.append(
            "Fintech capability:        "
            f"{scores['fintech_capability'].get('percentage', 0)}%"
        )
        lines.append(
            "AI capability:             "
            f"{scores['ai_capability'].get('percentage', 0)}%"
        )
        lines.append(
            "Production readiness:      "
            f"{scores['production_readiness'].get('percentage', 0)}%"
        )
        lines.append("")
        lines.append("MODE STATUS")

        for mode, status in report["final_status"].items():
            if mode in {
                "deployment_approved",
                "live_trading_approved",
            }:
                continue

            lines.append(
                f"{mode:<28} "
                f"{status['status']} "
                f"({status['remaining_workstreams']} workstreams)"
            )

        lines.append("")
        lines.append("PRIORITIZED ROOT WORKSTREAMS")

        for workstream in report["root_workstreams"]:
            lines.append("")
            lines.append(
                f"{workstream['order']:>2}. "
                f"[{workstream['classification']}] "
                f"{workstream['title']}"
            )
            lines.append(
                f"    ID: {workstream['workstream_id']}"
            )

            if workstream["dependencies"]:
                lines.append(
                    "    Depends on: "
                    + ", ".join(workstream["dependencies"])
                )
            else:
                lines.append(
                    "    Depends on: none"
                )

            lines.append(
                f"    Supporting findings: "
                f"{len(workstream['supporting_findings'])}"
            )

            lines.append("    Acceptance criteria:")

            for criterion in workstream[
                "acceptance_criteria"
            ]:
                lines.append(
                    f"      - {criterion}"
                )

        lines.append("")
        lines.append("PAPER-MODE PATH")

        for item in report["paper_mode_path"]:
            lines.append(
                f"- {item['order']}. "
                f"{item['title']}"
            )

        lines.append("")
        lines.append("AUTHENTICATED BROKER PATH")

        for item in report[
            "authenticated_broker_path"
        ]:
            lines.append(
                f"- {item['order']}. "
                f"{item['title']}"
            )

        lines.append("")
        lines.append("LIVE-TRADING PATH")

        for item in report["live_trading_path"]:
            lines.append(
                f"- {item['order']}. "
                f"{item['title']}"
            )

        lines.append("")
        lines.append("RELEASE GATES")

        for gate in report["release_gates"]:
            lines.append("")
            lines.append(
                f"{gate['gate']}: "
                f"{gate['status']}"
            )

            for requirement in gate["requirements"]:
                lines.append(
                    f"  - {requirement}"
                )

        lines.append("")
        lines.append("APPROVAL")
        lines.append("Deployment approved: NO")
        lines.append("Live trading approved: NO")
        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)

    def _build_workstreams(
        self,
        findings: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        results = []

        for rule in ROOT_CAUSE_RULES:
            matched = []

            for finding in findings:
                haystack = " ".join(
                    [
                        str(finding.get("title", "")),
                        str(finding.get("description", "")),
                        str(finding.get("domain", "")),
                    ]
                ).lower()

                if any(
                    keyword.lower() in haystack
                    for keyword in rule[
                        "finding_keywords"
                    ]
                ):
                    matched.append(finding)

            if not matched:
                continue

            mode_flags = {
                "blocks_paper_mode": any(
                    item.get(
                        "blocks_paper_mode",
                        False,
                    )
                    for item in matched
                ),
                "blocks_broker_integration": any(
                    item.get(
                        "blocks_broker_integration",
                        False,
                    )
                    for item in matched
                ),
                "blocks_live_trading": any(
                    item.get(
                        "blocks_live_trading",
                        False,
                    )
                    for item in matched
                ),
            }

            results.append(
                {
                    "workstream_id": rule["id"],
                    "title": rule["title"],
                    "classification": (
                        self._highest_classification(
                            matched,
                            default=rule[
                                "classification"
                            ],
                        )
                    ),
                    "dependencies": list(
                        rule["dependencies"]
                    ),
                    "acceptance_criteria": list(
                        rule["acceptance_criteria"]
                    ),
                    "supporting_findings": [
                        {
                            "finding_id": item.get(
                                "finding_id"
                            ),
                            "classification": item.get(
                                "classification"
                            ),
                            "domain": item.get("domain"),
                            "title": item.get("title"),
                            "evidence": item.get("evidence"),
                        }
                        for item in matched
                    ],
                    **mode_flags,
                }
            )

        return results

    def _dependency_order(
        self,
        workstreams: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        by_id = {
            item["workstream_id"]: item
            for item in workstreams
        }

        remaining = set(by_id)
        completed: set[str] = set()
        ordered = []

        while remaining:
            available = sorted(
                [
                    workstream_id
                    for workstream_id in remaining
                    if all(
                        dependency not in by_id
                        or dependency in completed
                        for dependency in by_id[
                            workstream_id
                        ]["dependencies"]
                    )
                ],
                key=lambda workstream_id: (
                    self._classification_order(
                        by_id[workstream_id][
                            "classification"
                        ]
                    ),
                    workstream_id,
                ),
            )

            if not available:
                available = sorted(
                    remaining,
                    key=lambda workstream_id: (
                        self._classification_order(
                            by_id[workstream_id][
                                "classification"
                            ]
                        ),
                        workstream_id,
                    ),
                )

            for workstream_id in available:
                item = dict(by_id[workstream_id])
                item["order"] = len(ordered) + 1
                ordered.append(item)
                completed.add(workstream_id)
                remaining.remove(workstream_id)

        return ordered

    @staticmethod
    def _mode_path(
        workstreams: list[dict[str, Any]],
        mode_field: str,
    ) -> list[dict[str, Any]]:
        return [
            {
                "order": item["order"],
                "workstream_id": item[
                    "workstream_id"
                ],
                "classification": item[
                    "classification"
                ],
                "title": item["title"],
                "acceptance_criteria": item[
                    "acceptance_criteria"
                ],
            }
            for item in workstreams
            if item.get(mode_field, False)
        ]

    @staticmethod
    def _mode_status(
        path: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return {
            "status": (
                "BLOCKED"
                if path
                else "ELIGIBLE_FOR_VALIDATION"
            ),
            "remaining_workstreams": len(path),
            "approved": False,
        }

    @staticmethod
    def _orphan_findings(
        findings: list[dict[str, Any]],
        workstreams: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        assigned = {
            item["finding_id"]
            for workstream in workstreams
            for item in workstream[
                "supporting_findings"
            ]
            if item.get("finding_id")
        }

        return [
            finding
            for finding in findings
            if finding.get("finding_id")
            not in assigned
        ]

    def _executive_summary(
        self,
        workstreams: list[dict[str, Any]],
        raw_findings: list[dict[str, Any]],
        orphan_findings: list[dict[str, Any]],
    ) -> dict[str, Any]:
        counts = Counter(
            item["classification"]
            for item in workstreams
        )

        return {
            "blocker_status": (
                self.blockers
                .get("summary", {})
                .get(
                    "overall_status",
                    "UNKNOWN",
                )
            ),
            "raw_finding_count": len(
                raw_findings
            ),
            "root_workstream_count": len(
                workstreams
            ),
            "orphan_finding_count": len(
                orphan_findings
            ),
            "critical_workstreams": counts.get(
                "CRITICAL_BLOCKER",
                0,
            ),
            "high_workstreams": counts.get(
                "HIGH_BLOCKER",
                0,
            ),
            "deferred_workstreams": counts.get(
                "DEFERRED_INTEGRATION",
                0,
            ),
            "maturity_workstreams": counts.get(
                "MATURITY_GAP",
                0,
            ),
            "statement": (
                "NeuroVest contains strong fintech capability and "
                "substantial AI capability, but production release remains "
                "blocked until root architecture, contract, safety, audit, "
                "verification, authentication, and broker-integration "
                "workstreams are completed and validated."
            ),
        }

    @staticmethod
    def _release_gates(
        workstreams: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        ids = {
            item["workstream_id"]
            for item in workstreams
        }

        return [
            {
                "gate": "PAPER_MODE_VALIDATION",
                "status": "BLOCKED",
                "requirements": [
                    "All paper-mode blocking workstreams completed.",
                    "Paper-trading end-to-end tests pass.",
                    "Risk and emergency-stop tests pass.",
                    "Deployment remains simulation-only.",
                ],
            },
            {
                "gate": "AUTHENTICATED_BROKER_VALIDATION",
                "status": (
                    "BLOCKED"
                    if {
                        "auth_identity",
                        "broker_integration",
                    }.intersection(ids)
                    else "ELIGIBLE_FOR_VALIDATION"
                ),
                "requirements": [
                    "Authentication lifecycle completed.",
                    "Secure credential handling verified.",
                    "SnapTrade reconnect and account-selection tests pass.",
                    "Live order submission remains disabled.",
                ],
            },
            {
                "gate": "LIVE_TRADING_CANDIDATE",
                "status": "BLOCKED",
                "requirements": [
                    "No critical or high blocker remains.",
                    "All deferred integrations completed.",
                    "Immutable audit ledger verified.",
                    "AI tool and safety boundaries verified.",
                    "Broker, risk, order, and reconciliation tests pass.",
                    "Separate explicit live-trading approval required.",
                ],
            },
        ]

    @staticmethod
    def _highest_classification(
        findings: list[dict[str, Any]],
        default: str,
    ) -> str:
        order = {
            "CRITICAL_BLOCKER": 0,
            "HIGH_BLOCKER": 1,
            "DEFERRED_INTEGRATION": 2,
            "MATURITY_GAP": 3,
            "INFORMATIONAL": 4,
        }

        classifications = [
            item.get(
                "classification",
                default,
            )
            for item in findings
        ]

        classifications.append(default)

        return min(
            classifications,
            key=lambda value: order.get(
                value,
                99,
            ),
        )

    @staticmethod
    def _classification_order(
        classification: str,
    ) -> int:
        return {
            "CRITICAL_BLOCKER": 0,
            "HIGH_BLOCKER": 1,
            "DEFERRED_INTEGRATION": 2,
            "MATURITY_GAP": 3,
            "INFORMATIONAL": 4,
        }.get(
            classification,
            99,
        )
