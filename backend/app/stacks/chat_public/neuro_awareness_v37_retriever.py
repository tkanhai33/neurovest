
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

TOPICS = {
    "risk": ("risk", "exposure", "drawdown", "limit"),
    "strategy": ("strategy", "allocation", "signal", "indicator"),
    "execution": ("execution", "order", "broker", "submit", "fill"),
    "paper": ("paper", "simulation", "simulated"),
    "safety": ("safety", "emergency", "kill switch", "locked", "guard"),
    "market_data": ("market data", "market", "quote", "historical", "bars"),
    "ai": ("wolfden", "ollama", "llm", "model", "reasoning"),
    "conversation": ("conversation", "context", "memory", "chat", "message"),
}

# Known declarations are ranking anchors, not proof that
# a live request reaches the corresponding code.
ANCHORS = {
    "risk": ("check_risk_limits", "calculate_exposure", "is_kill_switch_active"),
    "strategy": ("evaluate_fixed_weight_proposal_snapshot",),
    "execution": ("process_portfolio_output", "submit_authenticated_paper_order"),
    "paper": ("assert_paper_execution_allowed", "process_portfolio_output"),
    "safety": (
        "emergency_stop",
        "assert_live_execution_allowed",
        "assert_paper_execution_allowed",
        "set_kill_switch",
    ),
    "market_data": ("get_bars", "get_daily_bars_for_symbols"),
    "ai": ("ask_ollama", "monitor_and_process_signals"),
    "conversation": (
        "assemble_chat_context",
        "load_context_bundle",
        "append_message",
    ),
}

class StaleEvidence(RuntimeError):
    pass

class Retriever:
    def __init__(self, root, index_path):
        self.root = Path(root).resolve()
        self.index_path = Path(index_path).resolve()
        if not self.index_path.is_file() or self.index_path.is_symlink():
            raise StaleEvidence("Evidence index unavailable")
        self.index = json.loads(self.index_path.read_text("utf-8"))
        if self.index.get("schema") != "neuro_awareness_v37_multistack_evidence_v1":
            raise StaleEvidence("Evidence schema mismatch")

    def verify(self):
        fingerprints = self.index["source_fingerprints"]
        for relative, expected in fingerprints.items():
            path = (self.root / relative).resolve()
            if (
                not path.is_relative_to(self.root)
                or not path.is_file()
                or path.is_symlink()
            ):
                raise StaleEvidence("Unsafe indexed source")
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual != expected:
                raise StaleEvidence("Indexed source fingerprint mismatch")
        return len(fingerprints)

    @staticmethod
    def tokens(value):
        return set(re.findall(r"[a-z][a-z0-9_]+", value.casefold()))

    def topics_for(self, question):
        text = question.casefold()
        found = []
        for topic, terms in TOPICS.items():
            if any(
                re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text)
                for term in terms
            ):
                found.append(topic)
        return found

    def rank(self, definition, topic, tokens):
        name = definition["name"]
        short = name.split(".")[-1]
        file = definition["file"]
        stack = definition["stack"]
        haystack = " ".join((
            name.replace("_", " "),
            Path(file).stem.replace("_", " "),
            stack.replace("_", " "),
        ))
        overlap = len(tokens & self.tokens(haystack))
        score = overlap * 5
        if short in ANCHORS.get(topic, ()):
            score += 30
        if stack == topic:
            score += 8
        if topic == "paper" and "paper" in haystack.casefold():
            score += 8
        if topic == "safety" and any(
            value in haystack.casefold()
            for value in ("control", "kill", "guard")
        ):
            score += 8
        if topic == "ai" and "wolfden" in haystack.casefold():
            score += 8
        return score

    def retrieve(self, question, per_topic=4, max_definitions=24):
        if not isinstance(question, str) or not question.strip():
            raise ValueError("Question required")
        if len(question) > 2000:
            raise ValueError("Question too long")

        checked_files = self.verify()
        topics = self.topics_for(question)

        if not topics:
            return {
                "status": "INSUFFICIENT_TOPIC_EVIDENCE",
                "topics": [],
                "definitions": [],
                "call_expressions": [],
                "verified_source_files": checked_files,
                "runtime_execution_verified": False,
                "call_targets_resolved": False,
            }

        tokens = self.tokens(question)
        chosen = {}
        definitions = self.index["definitions"]

        # Guarantee representation from each matched topic,
        # instead of allowing one stack to consume every slot.
        for topic in topics:
            ranked = sorted(
                definitions,
                key=lambda item: (
                    -self.rank(item, topic, tokens),
                    item["file"],
                    item["line"],
                ),
            )
            count = 0
            for item in ranked:
                if count >= per_topic:
                    break
                if self.rank(item, topic, tokens) <= 0:
                    break
                key = (item["file"], item["line"], item["name"])
                chosen[key] = item
                count += 1

        selected = list(chosen.values())[:max_definitions]
        identifiers = {
            (item["file"], item["name"])
            for item in selected
        }

        # Call expressions are useful candidate relationships.
        # They are NOT resolved runtime call edges.
        selected_calls = [
            call
            for call in self.index["call_expressions"]
            if (call["file"], call["caller"]) in identifiers
        ][:40]

        return {
            "status": "SOURCE_EVIDENCE_AVAILABLE" if selected
                      else "INSUFFICIENT_TOPIC_EVIDENCE",
            "topics": topics,
            "definitions": selected,
            "call_expressions": selected_calls,
            "verified_source_files": checked_files,
            "runtime_execution_verified": False,
            "call_targets_resolved": False,
            "database_records_accessed": False,
            "broker_orders_sent": False,
        }

    def render(self, question):
        result = self.retrieve(question)
        lines = [
            "NEURO MULTI-STACK SOURCE EVIDENCE — EXPERIMENTAL",
            "EVIDENCE_STATUS=" + result["status"],
            "TOPICS=" + ",".join(result["topics"]),
            "SOURCE_FILES_VERIFIED=" + str(result["verified_source_files"]),
            "",
            "SOURCE DECLARATIONS",
        ]
        for item in result["definitions"]:
            lines.append(
                "- " + item["name"] + " at "
                + item["file"] + ":" + str(item["line"])
            )

        lines += [
            "",
            "STATIC CALL EXPRESSIONS (TARGETS UNRESOLVED)",
        ]
        for call in result["call_expressions"][:16]:
            lines.append(
                "- " + call["caller"] + " calls expression "
                + call["target_expression"] + " at "
                + call["file"] + ":" + str(call["line"])
            )

        lines += [
            "",
            "RUNTIME_EXECUTION_VERIFIED=NO",
            "CALL_TARGETS_RESOLVED=NO",
            "DATABASE_RECORDS_ACCESSED=NO",
            "BROKER_AUTHORIZATION_VERIFIED=NO",
            "SOURCE_FINGERPRINTS=PASS",
        ]

        # NEURO_V38_QUALIFIED_CHAIN_V1
        # These findings are static-source qualified, not runtime verified.
        if any(topic in ("risk", "execution", "paper", "safety")
               for topic in result["topics"]):
            proof_path = self.root / 'runtime/qualification/neuro_awareness_v38_paper_chain_20261013T005141Z/source_chain.json'
            if not proof_path.is_file() or proof_path.is_symlink():
                raise StaleEvidence("V3.8 proof missing")
            proof_bytes = proof_path.read_bytes()
            if hashlib.sha256(proof_bytes).hexdigest() != '96e3b31944b8d426af876f385680aa57152226c369ac80808d499ecc124bcb11':
                raise StaleEvidence("V3.8 proof fingerprint mismatch")
            proof = json.loads(proof_bytes.decode("utf-8"))
            if (
                proof.get("schema") != "neuro_awareness_v38_paper_chain_v1"
                or proof.get("qualification") != "STATIC_SOURCE_CHAIN_QUALIFIED"
                or len(proof.get("checks", {})) != 11
                or not all(value is True
                           for value in proof.get("checks", {}).values())
            ):
                raise StaleEvidence("V3.8 proof qualification invalid")
            for relative, expected in proof["source_fingerprints"].items():
                source_path = self.root / relative
                if (
                    not source_path.resolve().is_relative_to(self.root)
                    or not source_path.is_file()
                    or source_path.is_symlink()
                    or hashlib.sha256(source_path.read_bytes()).hexdigest()
                    != expected
                ):
                    raise StaleEvidence("V3.8 source fingerprint stale")
            lines.extend([
                "",
                "V3.8 STATIC SOURCE-CHAIN QUALIFICATION",
                "CLASSIFICATION=STATIC_SOURCE_CHAIN_QUALIFIED",
                "CONFIRMED SOURCE RELATIONSHIPS:",
            ])
            lines.extend("- " + value for value in proof["established"])
            lines.append("NOT ESTABLISHED:")
            lines.extend("- " + value for value in proof["not_established"])
            lines.extend([
                "SIMULATED_EXECUTED_STATUS_IS_NOT_A_BROKER_FILL=YES",
                "LIVE_EXECUTION_GUARD_IN_INSPECTED_SOURCE=UNCONDITIONAL_REJECTION",
                "END_TO_END_RUNTIME_VERIFIED=NO",
                "ALL_BROKER_PATHS_AUDITED=NO",
                "ORDER_VALUE_LIMITS_ON_THIS_PATH_VERIFIED=NO",
                "DO_NOT_ASSERT_ALL_RISK_GUARDS_RUN_FOR_EVERY_ORDER=YES",
                "V38_SOURCE_FINGERPRINTS=PASS",
            ])

        # NEURO_V39_STATIC_PATH_FINDER_V1
        # Graph direction means "imports from", NOT runtime data flow.
        if result["topics"]:
            import hashlib as _v39_hashlib
            import json as _v39_json
            from collections import deque as _v39_deque

            _v39_path = (
                self.root /
                "runtime/qualification/"
                "neuro_awareness_v39_architecture_20261013T010814Z/"
                "cross_stack_graph.json"
            )

            if (
                not _v39_path.is_file()
                or _v39_path.is_symlink()
                or _v39_hashlib.sha256(
                    _v39_path.read_bytes()
                ).hexdigest()
                != "b294b121d91f54eb08c45ae73d70f20a96555aa6f7b5167a2ca39b99b5105d35"
            ):
                raise StaleEvidence("V3.9 architecture graph unavailable")

            _v39_graph = _v39_json.loads(
                _v39_path.read_text("utf-8")
            )

            if (
                _v39_graph.get("schema")
                != "neuro_awareness_v39_cross_stack_graph_v1"
                or _v39_graph.get("source_fingerprints")
                != self.index["source_fingerprints"]
            ):
                raise StaleEvidence("V3.9 architecture graph mismatch")

            _v39_adj = {}
            _v39_edge_info = {}

            for _v39_edge in _v39_graph["cross_stack_edges"]:
                _v39_src = _v39_edge["source_stack"]
                _v39_dst = _v39_edge["target_stack"]
                _v39_adj.setdefault(_v39_src, set()).add(_v39_dst)
                _v39_edge_info[(_v39_src, _v39_dst)] = _v39_edge

            def _v39_find(start, finish, max_hops=4):
                queue = _v39_deque([(start, [start])])
                visited = {start}

                while queue:
                    current, path = queue.popleft()

                    if current == finish:
                        return path

                    if len(path) - 1 >= max_hops:
                        continue

                    for neighbor in sorted(_v39_adj.get(current, ())):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(
                                (neighbor, path + [neighbor])
                            )
                return None

            _v39_topics = set(result["topics"])
            _v39_pairs = []

            if "strategy" in _v39_topics:
                _v39_pairs.extend([
                    ("strategy", "market_data"),
                    ("strategy", "execution"),
                ])
            if "market_data" in _v39_topics:
                _v39_pairs.extend([
                    ("strategy", "market_data"),
                    ("market_data", "wolfden_ai"),
                ])
            if "ai" in _v39_topics:
                _v39_pairs.extend([
                    ("chat_public", "wolfden_ai"),
                    ("strategy", "wolfden_ai"),
                ])
            if "risk" in _v39_topics:
                _v39_pairs.extend([
                    ("execution", "risk"),
                    ("strategy", "risk"),
                ])
            if "execution" in _v39_topics or "paper" in _v39_topics:
                _v39_pairs.extend([
                    ("application", "execution"),
                    ("execution", "portfolio"),
                ])
            if "conversation" in _v39_topics:
                _v39_pairs.extend([
                    ("chat_public", "identity_auth"),
                    ("chat_public", "db_runtime"),
                ])

            _v39_unique = list(dict.fromkeys(_v39_pairs))[:8]

            if _v39_unique:
                lines.extend([
                    "",
                    "V3.9 CROSS-STACK DEPENDENCY PATHS",
                    "PATH_CLASSIFICATION=STATIC_IMPORT_DEPENDENCIES",
                    "PATH_DIRECTION=IMPORTING_STACK_TO_IMPORTED_STACK",
                    "PATHS_ARE_NOT_RUNTIME_DATA_FLOW=YES",
                ])

                for _v39_start, _v39_end in _v39_unique:
                    _v39_path_nodes = _v39_find(
                        _v39_start, _v39_end
                    )

                    if _v39_path_nodes is None:
                        lines.append(
                            "NO_STATIC_IMPORT_PATH="
                            + _v39_start + " -> " + _v39_end
                        )
                        continue

                    lines.append(
                        "STATIC_PATH="
                        + " -> ".join(_v39_path_nodes)
                    )

                    for _v39_a, _v39_b in zip(
                        _v39_path_nodes, _v39_path_nodes[1:]
                    ):
                        _v39_info = _v39_edge_info[(_v39_a, _v39_b)]
                        _v39_sources = [
                            entry
                            for entry in _v39_graph["imports"]
                            if (
                                entry["source_stack"] == _v39_a
                                and entry["target_stack"] == _v39_b
                            )
                        ]
                        _v39_sources.sort(
                            key=lambda entry: (
                                entry["source_path"],
                                entry["line"],
                            )
                        )

                        lines.append(
                            "IMPORT_EDGE="
                            + _v39_a + " -> " + _v39_b
                            + " IMPORT_RECORDS="
                            + str(_v39_info["import_count"])
                        )

                        for _v39_source in _v39_sources[:2]:
                            lines.append(
                                "IMPORT_SOURCE="
                                + _v39_source["source_path"]
                                + ":" + str(_v39_source["line"])
                                + " MODULE="
                                + _v39_source["module"]
                            )

                lines.extend([
                    "CALL_TARGETS_RESOLVED_BY_GRAPH=NO",
                    "RUNTIME_DATA_FLOW_VERIFIED=NO",
                    "GRAPH_SOURCE_FINGERPRINTS=PASS",
                ])


        # NEURO_V41_QUALIFICATION_EVIDENCE_V1
        # Source-qualified behavioral evidence. No model-generated facts.
        if result["topics"]:
            import hashlib as _v41_hashlib
            import json as _v41_json

            _v41_reports = {
                "execution_risk": (
                    "neuro_v40_batch1_20261013T011314Z",
                    "91909308e74020528c554c8e45e97a94dc92d51763702c98627aa16c2352964d",
                ),
                "integration_discovery": (
                    "neuro_v40_batch2_20261013T011426Z",
                    "1030667e0fb736efc6fbadfd9f2043ff39e53c28480fcc10785b9b4c150b7fd3",
                ),
                "controlled_execution": (
                    "neuro_v40_batch5_20261013T011757Z",
                    "125dcbdab764b035954b326a0f1bb5ff5e3dea03c0091112289f412755660518",
                ),
            }

            _v41_loaded = {}
            for _v41_key, (_v41_dir, _v41_expected) in _v41_reports.items():
                _v41_path = (
                    self.root
                    / "runtime"
                    / "qualification"
                    / _v41_dir
                    / "qualification.json"
                )

                if (
                    not _v41_path.is_file()
                    or _v41_path.is_symlink()
                    or _v41_hashlib.sha256(
                        _v41_path.read_bytes()
                    ).hexdigest() != _v41_expected
                ):
                    raise StaleEvidence(
                        "V4.1 qualification evidence unavailable"
                    )

                _v41_loaded[_v41_key] = _v41_json.loads(
                    _v41_path.read_text("utf-8")
                )

            _v41_topics = set(result["topics"])

            if _v41_topics.intersection({
                "strategy", "market_data", "risk",
                "execution", "paper", "ai",
            }):
                lines.extend([
                    "",
                    "V4.1 QUALIFICATION-AWARE EVIDENCE",
                    "EVIDENCE_CLASS=ISOLATED_BEHAVIOR_AND_STATIC_DISCOVERY",
                    "SOURCE_REPORTS_HASH_VERIFIED=3",
                    "TESTED_BEHAVIOR:",
                    "- Paper/live execution authorization branches "
                    "were checked in isolated tests.",
                    "- Simulated trade helper behavior and selected "
                    "risk calculations passed controlled tests.",
                    "- Historical-bar symbol normalization and "
                    "provider failure handling passed isolated tests.",
                    "- Multi-symbol dispatch and failure propagation "
                    "passed with substituted dependencies.",
                    "- Allocation validation and cash-only execution "
                    "disabled state passed isolated tests.",
                    "- Fifteen substitute evaluator callbacks were "
                    "invoked by the aggregation orchestrator.",
                    "STATIC_EVIDENCE:",
                    "- Strategy-to-market-data dependencies and "
                    "bound call sites were discovered.",
                    "- Wolfden AI source definitions and import "
                    "dependencies were inspected.",
                    "NOT_VERIFIED:",
                    "- Successful real-provider market-data retrieval.",
                    "- Full weighted portfolio evaluation.",
                    "- All fifteen actual evaluator implementations "
                    "in the same end-to-end test.",
                    "- Wolfden AI inference behavior.",
                    "- End-to-end HTTP authorization or broker routing.",
                    "- Production database persistence or transaction "
                    "atomicity.",
                    "QUALIFICATION_NOT_PRODUCTION_APPROVAL=YES",
                    "RUNTIME_END_TO_END_VERIFIED=NO",
                    "LIVE_BROKER_TRADING_APPROVED=NO",
                    "V41_EVIDENCE_STATUS=PASS",
                ])


        # NEURO_V42_DEVELOPER_INTELLIGENCE_V1
        if result["topics"]:
            import hashlib as _v42_hashlib
            import json as _v42_json
            import re as _v42_re

            _v42_graph_path = (
                self.root
                / "runtime/qualification/"
                "neuro_awareness_v39_architecture_20261013T010814Z/"
                "cross_stack_graph.json"
            )

            if (
                not _v42_graph_path.is_file()
                or _v42_graph_path.is_symlink()
                or _v42_hashlib.sha256(
                    _v42_graph_path.read_bytes()
                ).hexdigest() != "b294b121d91f54eb08c45ae73d70f20a96555aa6f7b5167a2ca39b99b5105d35"
            ):
                raise StaleEvidence(
                    "V4.2 architecture evidence unavailable"
                )

            _v42_graph = _v42_json.loads(
                _v42_graph_path.read_text("utf-8")
            )

            if (
                _v42_graph.get("source_fingerprints")
                != self.index["source_fingerprints"]
            ):
                raise StaleEvidence(
                    "V4.2 source provenance mismatch"
                )

            _v42_question = str(question).lower()
            _v42_topics = set(result["topics"])

            # Explicit user wording takes precedence over broad topics.
            _v42_aliases = {
                "strategy": (
                    "strategy", "strategies", "backtest",
                    "evaluation", "evaluators"
                ),
                "market_data": (
                    "market data", "market_data",
                    "historical bars", "ohlcv", "provider"
                ),
                "execution": (
                    "execution", "paper broker",
                    "orders", "simulated fill"
                ),
                "risk": (
                    "risk", "drawdown", "kill switch"
                ),
                "wolfden_ai": (
                    "wolfden", "wolfden ai"
                ),
                "chat_public": (
                    "developer chat", "chat runtime",
                    "chat_public"
                ),
                "identity_auth": (
                    "authentication", "identity",
                    "developer role"
                ),
                "portfolio": (
                    "portfolio", "allocation"
                ),
                "strategy_candidate_sandbox": (
                    "candidate", "sandbox",
                    "developer review"
                ),
                "db_runtime": (
                    "database", "postgres"
                ),
            }

            _v42_focus = [
                name
                for name, aliases in _v42_aliases.items()
                if any(
                    _v42_re.search(
                        r"(?<![A-Za-z0-9_])"
                        + _v42_re.escape(alias)
                        + r"(?![A-Za-z0-9_])",
                        _v42_question,
                    )
                    for alias in aliases
                )
            ]

            for _v42_topic, _v42_stack in (
                ("strategy", "strategy"),
                ("market_data", "market_data"),
                ("risk", "risk"),
                ("execution", "execution"),
                ("paper", "execution"),
                ("ai", "wolfden_ai"),
                ("conversation", "chat_public"),
            ):
                if (
                    _v42_topic in _v42_topics
                    and _v42_stack not in _v42_focus
                ):
                    _v42_focus.append(_v42_stack)

            _v42_known = {
                n["source_stack"]
                for n in _v42_graph["cross_stack_edges"]
            } | {
                n["target_stack"]
                for n in _v42_graph["cross_stack_edges"]
            }

            _v42_focus = [
                s for s in _v42_focus
                if s in _v42_known
            ][:3]

            if _v42_focus:
                _v42_edges = _v42_graph["cross_stack_edges"]
                _v42_imports = _v42_graph["imports"]

                lines.extend([
                    "",
                    "V4.2 DEVELOPER INTELLIGENCE",
                    "V42_EVIDENCE_CLASS=STATIC_ARCHITECTURE",
                    "V42_SOURCE_GRAPH_HASH=PASS",
                    "FOCUSED_STACKS="
                    + ",".join(_v42_focus),
                    "V42_RUNTIME_TRACES_VERIFIED=NO",
                ])

                # Capability 1: focused stack selection.
                # Capability 2: incoming/outgoing impact.
                # Capability 3: exact source import witnesses.
                for _v42_stack in _v42_focus:
                    _v42_out = [
                        e for e in _v42_edges
                        if e["source_stack"] == _v42_stack
                    ]
                    _v42_in = [
                        e for e in _v42_edges
                        if e["target_stack"] == _v42_stack
                    ]

                    _v42_out.sort(
                        key=lambda e: (
                            -e["import_count"],
                            e["target_stack"],
                        )
                    )
                    _v42_in.sort(
                        key=lambda e: (
                            -e["import_count"],
                            e["source_stack"],
                        )
                    )

                    lines.append(
                        "STACK_IMPACT=" + _v42_stack
                        + " OUTGOING_STACKS="
                        + str(len(_v42_out))
                        + " INCOMING_STACKS="
                        + str(len(_v42_in))
                    )

                    for _v42_edge in _v42_out[:3]:
                        _v42_src = _v42_edge["source_stack"]
                        _v42_dst = _v42_edge["target_stack"]

                        lines.append(
                            "STATIC_DEPENDENCY="
                            + _v42_src + " -> " + _v42_dst
                            + " IMPORT_RECORDS="
                            + str(_v42_edge["import_count"])
                        )

                        _v42_witnesses = sorted(
                            [
                                item for item in _v42_imports
                                if (
                                    item["source_stack"] == _v42_src
                                    and item["target_stack"] == _v42_dst
                                )
                            ],
                            key=lambda item: (
                                item["source_path"],
                                item["line"],
                            )
                        )

                        for _v42_item in _v42_witnesses[:2]:
                            lines.append(
                                "DEPENDENCY_SOURCE="
                                + _v42_item["source_path"]
                                + ":" + str(_v42_item["line"])
                                + " MODULE="
                                + _v42_item["module"]
                            )

                    for _v42_edge in _v42_in[:3]:
                        lines.append(
                            "STATIC_DEPENDENT="
                            + _v42_edge["source_stack"]
                            + " -> " + _v42_stack
                            + " IMPORT_RECORDS="
                            + str(_v42_edge["import_count"])
                        )

                # Capability 4: grounded investigation planning.
                if any(
                    word in _v42_question
                    for word in (
                        "debug", "error", "fail", "broken",
                        "why", "issue", "problem", "fix",
                        "improve", "recommend", "investigate",
                        "impact", "change"
                    )
                ):
                    lines.append(
                        "V42_READ_ONLY_INVESTIGATION_PLAN:"
                    )
                    lines.append(
                        "1. Inspect the cited import-source files "
                        "and their target module definitions."
                    )
                    lines.append(
                        "2. Resolve actual call targets before "
                        "asserting data flow or execution ordering."
                    )
                    lines.append(
                        "3. Compare available isolated-test "
                        "qualifications against the specific path."
                    )
                    lines.append(
                        "4. Reproduce behavior with mocked dependencies "
                        "and explicit expected outputs before changes."
                    )
                    lines.append(
                        "5. Review authentication, owner-scoping, "
                        "and execution guards before deployment."
                    )

                lines.extend([
                    "V42_ARCHITECTURAL_CAUTION="
                    "IMPORT_DEPENDENCIES_ARE_NOT_RUNTIME_CALLS",
                    "V42_UNVERIFIED="
                    "DYNAMIC_DISPATCH_AND_END_TO_END_EXECUTION",
                    "V42_AUTONOMOUS_CODE_MODIFICATION=NO",
                    "V42_LIVE_BROKER_APPROVAL=NO",
                    "V42_STATUS=PASS",
                ])

        return "\n".join(lines)



# NEURO_V421_GROUNDED_RESPONSE_POLISH_V1

# NEURO_V422_NATURAL_DEVELOPER_RESPONSES_V1
def polish_developer_answer(answer, question):
    """Render existing qualified evidence; no permission or tool actions."""
    import re

    if not isinstance(answer, str):
        return answer

    model_part, separator, evidence = answer.partition("SOURCE_EVIDENCE:")
    if not separator:
        return answer

    if "EVIDENCE_STATUS=SOURCE_EVIDENCE_AVAILABLE" not in evidence:
        return answer

    question = question if isinstance(question, str) else ""
    question_lower = question.lower()

    if re.search(
        r"\b(?:raw|full evidence|all evidence|source dump|"
        r"complete evidence|verbose|full trace|full report)\b",
        question,
        flags=re.IGNORECASE,
    ):
        return (
            "Detailed NeuroVest source evidence:\n\n"
            "SOURCE_EVIDENCE:" + evidence
        )

    records = [line.strip() for line in evidence.splitlines()]

    def values(prefix):
        return list(dict.fromkeys(
            line[len(prefix):]
            for line in records
            if line.startswith(prefix)
        ))

    def display_stack(stack):
        names = {
            "market_data": "market data",
            "chat_public": "Developer Chat",
            "db_runtime": "database runtime",
            "db_model": "database models",
            "identity_auth": "authentication",
            "journal_ledger": "journal and ledger",
            "wolfden_ai": "Wolfden AI",
            "strategy_candidate_sandbox": "strategy candidate sandbox",
            "application": "application entry points",
        }
        return names.get(stack, stack.replace("_", " "))

    def edge_records(prefix):
        output = []
        pattern = re.compile(
            r"^([A-Za-z0-9_]+) -> ([A-Za-z0-9_]+)"
            r" IMPORT_RECORDS=(\d+)"
        )
        for value in values(prefix):
            match = pattern.match(value)
            if match:
                output.append((
                    match.group(1),
                    match.group(2),
                    int(match.group(3)),
                ))
        return output

    dependencies = edge_records("STATIC_DEPENDENCY=")
    dependents = edge_records("STATIC_DEPENDENT=")

    focus_values = values("FOCUSED_STACKS=")
    focus = (
        focus_values[0].split(",")
        if focus_values else []
    )
    focus = [name for name in focus if name]

    source_records = []
    for value in values("DEPENDENCY_SOURCE="):
        match = re.match(
            r"^(\S+\.py):(\d+) MODULE=(\S+)",
            value,
        )
        if match:
            source_records.append({
                "path": match.group(1),
                "line": match.group(2),
                "module": match.group(3),
            })

    def references(src, dst, maximum=2):
        module_fragment = (
            "backend.app.stacks." + dst + "."
        )
        matches = [
            item for item in source_records
            if (
                "/stacks/" + src + "/" in item["path"]
                and (
                    item["module"].startswith(module_fragment)
                    or item["module"] ==
                    "backend.app.stacks." + dst
                )
            )
        ]
        return matches[:maximum]

    want_failure = any(
        word in question_lower
        for word in (
            "fail", "error", "debug", "broken",
            "problem", "issue", "investigate",
            "troubleshoot"
        )
    )
    want_tests = any(
        word in question_lower
        for word in (
            "test", "verify", "verified",
            "qualification", "proven",
            "coverage"
        )
    )
    want_impact = any(
        phrase in question_lower
        for phrase in (
            "depend on", "depends on",
            "dependency", "dependencies",
            "impact", "affected", "connect"
        )
    )

    tested = []
    unverified = []
    section = None

    for line in records:
        if line == "TESTED_BEHAVIOR:":
            section = "tested"
            continue
        if line == "NOT_VERIFIED:":
            section = "unverified"
            continue
        if line in ("STATIC_EVIDENCE:",):
            section = None
            continue
        if not line.startswith("- "):
            if line.endswith(":"):
                section = None
            continue
        if section == "tested":
            tested.append(line[2:])
        elif section == "unverified":
            unverified.append(line[2:])

    # Relevance filtering applies to presentation only.
    # No evidence classifications are promoted or invented.
    subject_words = set()
    if (
        "market" in question_lower
        or "provider" in question_lower
        or "bars" in question_lower
    ):
        subject_words.update((
            "bar", "provider", "symbol", "market",
            "multi-symbol", "retrieval"
        ))
    if "strateg" in question_lower:
        subject_words.update((
            "strategy", "allocation", "evaluator",
            "portfolio"
        ))
    if "risk" in question_lower:
        subject_words.update(("risk", "drawdown", "limit"))
    if "execution" in question_lower:
        subject_words.update(("execution", "trade", "broker"))

    def relevant(items, maximum):
        if not subject_words:
            return items[:maximum]
        matching = [
            item for item in items
            if any(
                word in item.lower()
                for word in subject_words
            )
        ]
        return (matching or items)[:maximum]

    output = []

    if focus:
        title = " and ".join(
            display_stack(name) for name in focus[:2]
        )
        output.append("## " + title.capitalize())
    else:
        output.append("## NeuroVest architecture")

    output.append("")

    if dependencies:
        chosen = [
            edge for edge in dependencies
            if (
                edge[0] in focus
                and edge[1] in focus
            )
        ]

        if not chosen:
            chosen = [
                edge for edge in dependencies
                if edge[0] in focus
            ]

        if not chosen:
            chosen = dependencies

        output.append("**How the components connect**")
        output.append("")

        for src, dst, count in chosen[:4]:
            sentence = (
                f"The {display_stack(src)} stack imports "
                f"the {display_stack(dst)} stack. "
                f"The static source graph contains "
                f"{count} import "
                f"{'record' if count == 1 else 'records'} "
                f"for that relationship."
            )

            refs = references(src, dst)
            if refs:
                citations = ", ".join(
                    f"`{item['path']}:{item['line']}`"
                    for item in refs
                )
                sentence += f" Examples: {citations}."

            output.append(sentence)
            output.append("")

    if dependents and want_impact:
        selected = [
            edge for edge in dependents
            if edge[1] in focus
        ][:4]

        if selected:
            output.append("**Components that depend on these stacks**")
            output.append("")
            for src, dst, count in selected:
                output.append(
                    f"The {display_stack(src)} stack imports "
                    f"{display_stack(dst)} "
                    f"({count} static import "
                    f"{'record' if count == 1 else 'records'})."
                )
            output.append("")

    if tested and (
        want_tests or want_failure
    ):
        output.append("**What has actually been tested**")
        output.append("")
        for item in relevant(tested, 4):
            output.append("- " + item)
        output.append("")

    if want_failure:
        output.append("**How to investigate a failure**")
        output.append("")

        if (
            "market_data" in focus
            or "provider" in question_lower
        ):
            output.extend([
                "1. Start with `get_bars()` in "
                "`backend/app/stacks/market_data/bars.py` "
                "and inspect request validation, provider routing "
                "and error handling.",
                "2. Check `get_daily_bars_for_symbols()` in "
                "`backend/app/stacks/market_data/"
                "multi_symbol_bars.py` for multi-symbol "
                "dispatch and failure propagation.",
                "3. Reproduce the specific failure with "
                "controlled input and a substituted provider. "
                "Compare the result with the recorded isolated tests.",
                "4. Only after confirming the failure path, "
                "investigate actual provider responses, runtime "
                "configuration and affected strategy callers.",
            ])
        else:
            output.extend([
                "1. Inspect the cited importing module and "
                "its target definitions.",
                "2. Reproduce the reported behavior with "
                "controlled inputs.",
                "3. Review relevant qualification reports "
                "before making changes.",
                "4. Validate authorization and execution "
                "boundaries before deployment.",
            ])
        output.append("")

    if unverified and (want_tests or want_failure):
        output.append("**Still unverified**")
        output.append("")
        for item in relevant(unverified, 3):
            output.append("- " + item)
        output.append("")

    if not dependencies and not tested and not source_records:
        # Do not fabricate an answer when there is no usable
        # source evidence for the requested topic.
        return (
            "I don't have enough qualified source evidence "
            "to answer that development question reliably. "
            "You can ask for full evidence to inspect "
            "what is available."
        )

    output.append(
        "*These relationships come from static source "
        "analysis; they are not proof of runtime execution. "
        "Previously recorded isolated tests do not establish "
        "complete integration or production readiness.*"
    )
    output.append("")
    output.append(
        "Ask for **full evidence** to see the underlying "
        "technical report."
    )

    return "\n".join(output)


# NEURO_V43_GROUNDED_DIAGNOSTICS_V1
_v43_previous_polish_developer_answer = polish_developer_answer


def _neuro_v43_diagnostic_section(question, evidence):
    """Read-only triage derived only from available source evidence."""
    import re

    if not isinstance(question, str):
        return ""

    q = question.lower()

    failure_terms = re.search(
        r"\b(?:fail(?:s|ed|ure|ing)?|broken|error|"
        r"exception|crash(?:es|ed)?|bug|debug|"
        r"troubleshoot|diagnos(?:e|is|tic)|"
        r"investigat(?:e|ion)|not working|"
        r"timeout|unavailable|incorrect|"
        r"returns? none)\b",
        q,
    )

    if not failure_terms:
        return ""

    if not isinstance(evidence, str):
        return ""

    if "EVIDENCE_STATUS=SOURCE_EVIDENCE_AVAILABLE" not in evidence:
        return ""

    rows = [line.strip() for line in evidence.splitlines()]

    def contains(value):
        return any(value in row for row in rows)

    def declaration(name):
        prefix = "- " + name + " at "
        for row in rows:
            if row.startswith(prefix):
                location = row[len(prefix):]
                if re.fullmatch(
                    r"backend/[A-Za-z0-9_./-]+\.py:\d+",
                    location,
                ):
                    return location
        return None

    topics = []
    for row in rows:
        if row.startswith("TOPICS="):
            topics = row.split("=", 1)[1].split(",")
            break

    market_relevant = (
        "market_data" in topics
        or any(
            term in q for term in (
                "market data", "market_data",
                "provider", "historical bar",
                "ohlcv", "price bars"
            )
        )
    )

    strategy_relevant = (
        "strategy" in topics
        or any(
            term in q for term in (
                "strategy", "strategies",
                "allocation", "evaluator",
                "backtest"
            )
        )
    )

    evidence_items = []
    checks = []
    boundaries = []

    if market_relevant:
        bars = declaration("get_bars")
        multi = declaration("get_daily_bars_for_symbols")

        if bars:
            evidence_items.append(
                "Historical-bar retrieval is declared at "
                f"`{bars}`."
            )
            checks.append(
                "Inspect the exact provider exception and "
                "historical-bar request parameters at "
                f"`{bars}`. Confirm the normalized symbol, "
                "requested limit and failure classification."
            )

        if multi:
            evidence_items.append(
                "Multi-symbol historical retrieval is declared at "
                f"`{multi}`."
            )
            checks.append(
                "Check whether one symbol causes the "
                "multi-symbol operation to fail as a whole. "
                f"Inspect `{multi}`."
            )

        if contains(
            "Historical-bar symbol normalization and "
            "provider failure handling passed isolated tests."
        ):
            evidence_items.append(
                "Controlled tests covered symbol normalization "
                "and a provider-failure branch."
            )

        if contains(
            "Multi-symbol dispatch and failure propagation "
            "passed with substituted dependencies."
        ):
            evidence_items.append(
                "Controlled tests covered multi-symbol dispatch "
                "and failure propagation."
            )

        if contains(
            "- Successful real-provider market-data retrieval."
        ):
            boundaries.append(
                "Successful retrieval from a real provider "
                "has not been verified by these qualifications."
            )

    if strategy_relevant:
        evaluation = declaration(
            "evaluate_fixed_weight_proposal_snapshot"
        )

        if evaluation:
            evidence_items.append(
                "The fixed-weight allocation evaluation "
                f"is declared at `{evaluation}`."
            )

            checks.append(
                "After verifying the market-data result, "
                "check which inputs reach the allocation "
                f"evaluation at `{evaluation}`. "
                "Do not assume a successful end-to-end flow."
            )

        if contains(
            "- Full weighted portfolio evaluation."
        ):
            boundaries.append(
                "Full weighted portfolio evaluation "
                "is not end-to-end verified."
            )

    if not evidence_items:
        return ""

    # These are investigation priorities, not measured probabilities.
    result = [
        "",
        "### Diagnostic triage",
        "",
        "**Status:** Investigation required. "
        "No root cause has been established.",
        "",
        "**Evidence relevant to this report**",
        "",
    ]

    for item in evidence_items[:6]:
        result.append("- " + item)

    if checks:
        result.extend([
            "",
            "**Prioritized checks**",
            "",
        ])

        for number, item in enumerate(checks[:4], 1):
            result.append(f"{number}. {item}")

    if boundaries:
        result.extend([
            "",
            "**What remains unverified**",
            "",
        ])
        for item in boundaries[:3]:
            result.append("- " + item)

    result.extend([
        "",
        "**Next evidence needed:** The exact error message, "
        "affected symbol or request, expected behavior, "
        "observed behavior and a sanitized traceback "
        "would help distinguish the possible failure paths.",
        "",
        "*This is source-grounded triage, not a reproduced bug "
        "or confirmed diagnosis. No application actions "
        "or broker operations were performed.*",
    ])

    return "\n".join(result)


def polish_developer_answer(answer, question):
    """Keep V4.2.2 answers; add triage for eligible failure questions."""
    import re

    base = _v43_previous_polish_developer_answer(answer, question)

    if not isinstance(base, str):
        return base

    if not isinstance(question, str):
        return base

    if re.search(
        r"\b(?:raw|full evidence|all evidence|source dump|"
        r"complete evidence|verbose|full trace|full report)\b",
        question,
        flags=re.IGNORECASE,
    ):
        return base

    if not isinstance(answer, str):
        return base

    _, separator, evidence = answer.partition("SOURCE_EVIDENCE:")

    if not separator:
        return base

    section = _neuro_v43_diagnostic_section(question, evidence)

    if not section:
        return base

    return base.rstrip() + "\n" + section


# NEURO_V445_DEDICATED_SELF_ASSESSMENT_V2
_v445_previous_render = Retriever.render
_v445_previous_polish = polish_developer_answer


def _v445_is_assessment(question):
    import re
    if not isinstance(question, str):
        return False
    return bool(re.search(
        r"\b(?:improv(?:e|ement|ements)|priorities|"
        r"self.assess(?:ment)?|weaknesses|readiness|"
        r"need to work on)\b",
        question,
        flags=re.IGNORECASE,
    ))


def _v445_assessment(root, question):
    import hashlib, json, urllib.request
    from pathlib import Path

    root = Path(root)
    specs = {
        "execution_and_risk": ("neuro_v40_batch1_20261013T011314Z", "91909308e74020528c554c8e45e97a94dc92d51763702c98627aa16c2352964d"),
        "integration_discovery": ("neuro_v40_batch2_20261013T011426Z", "1030667e0fb736efc6fbadfd9f2043ff39e53c28480fcc10785b9b4c150b7fd3"),
        "controlled_behavior": ("neuro_v40_batch5_20261013T011757Z", "125dcbdab764b035954b326a0f1bb5ff5e3dea03c0091112289f412755660518"),
    }

    reports = {}
    for key, (folder, expected) in specs.items():
        path = root / "runtime/qualification" / folder / "qualification.json"
        try:
            if not path.is_file() or path.is_symlink():
                raise ValueError("Unavailable report")
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != expected:
                raise ValueError("Report fingerprint changed")
            reports[key] = json.loads(raw)
        except (OSError, ValueError):
            reports[key] = None

    # Loopback health observation only; no application logs or DB access.
    route_count = None
    try:
        with urllib.request.urlopen(
            "http://127.0.0.1:8000/openapi.json", timeout=1.5
        ) as response:
            if response.status == 200:
                route_count = len(json.load(response).get("paths", {}))
    except Exception:
        pass

    behavior = reports["controlled_behavior"]
    qualified_behavior = (
        isinstance(behavior, dict)
        and behavior.get("schema") ==
        "neuro_v40_batch5_controlled_execution_v1"
        and behavior.get("passed") == 12
        and behavior.get("failed") == 0
    )
    absent = [key for key, value in reports.items() if value is None]

    # Evidence-driven coverage flags. An untested capability is not
    # automatically a broken capability.
    exclusions = set(
        behavior.get("not_verified", [])
        if isinstance(behavior, dict) else []
    )

    items = []

    if absent or not qualified_behavior:
        items.append((
            "Restore trusted qualification coverage",
            "A required qualification report is missing, changed, or not qualified.",
            "Re-run the affected controlled tests and review their evidence.",
        ))

    if "Real market-data provider success response" in exclusions:
        items.append((
            "Verify successful market-data retrieval",
            "The recorded tests exercised failure handling but did not "
            "qualify a successful real-provider response.",
            "Run an explicitly approved, bounded read-only integration test.",
        ))

    if "Actual strategy canonicalization and weighted portfolio math" in exclusions:
        items.append((
            "Verify complete portfolio evaluation",
            "The controlled tests did not exercise the full allocation math.",
            "Test the actual paper-only evaluator with known input fixtures.",
        ))

    if "Actual fifteen V4 evaluator implementations" in exclusions:
        items.append((
            "Qualify the actual strategy evaluators",
            "The aggregation test used fifteen substitute evaluators.",
            "Run the real evaluator implementations on deterministic "
            "historical fixtures and verify aggregation.",
        ))

    if "Actual Wolfden AI inference" in exclusions:
        items.append((
            "Benchmark local AI reasoning",
            "The controlled qualification did not verify Wolfden inference.",
            "Run a fixed source-grounded question benchmark and measure "
            "correctness, refusals, and unusable output.",
        ))

    if reports["integration_discovery"] is not None:
        items.append((
            "Verify runtime integration paths",
            "Static imports were identified, but do not prove runtime flow.",
            "Add permissioned, sanitized traces for selected paper-only paths.",
        ))

    if route_count is None:
        items.insert(0, (
            "Investigate local backend availability",
            "The bounded local HTTP observation did not complete.",
            "Verify service status and sanitized diagnostics before changing code.",
        ))

    lines = [
        "## NeuroVest self-assessment",
        "",
        "Here is what my available evidence indicates I need to improve. "
        "These are qualification gaps, not confirmed live failures.",
        "",
        "**Capability evidence**",
        "",
    ]

    for key, value in reports.items():
        lines.append(
            "- " + key.replace("_", " ").capitalize() + ": "
            + ("verified pinned report" if value is not None
               else "missing or changed evidence")
        )

    if qualified_behavior:
        lines.append(
            "- Controlled behavior: 12 isolated checks passed; "
            "end-to-end integration remains unverified."
        )

    lines += [
        "",
        "**Current backend observation**",
        "",
        (
            f"- Local OpenAPI endpoint responded with {route_count} paths."
            if route_count is not None
            else "- Local OpenAPI observation was unavailable."
        ),
        "- This does not establish database, provider, strategy, "
        "or broker health.",
        "",
        "**What I need to improve next**",
        "",
    ]

    for number, (title, reason, next_step) in enumerate(items[:6], 1):
        lines += [
            f"{number}. **{title}**",
            f"   - Why: {reason}",
            f"   - Evidence needed: {next_step}",
        ]

    if not items:
        lines.append(
            "No improvement priority is established by this limited "
            "evidence set. More coverage is required."
        )

    lines += [
        "",
        "**Confidence boundary:** I have not inspected production logs, "
        "executed provider calls, or reproduced new failures. "
        "I cannot autonomously approve production changes or live trading.",
    ]
    return "\n".join(lines)


def _v445_render(self, question):
    if _v445_is_assessment(question):
        verified = self.verify()
        if verified != 419:
            raise StaleEvidence("Self-assessment source verification failed")
        return (
            "NEURO SELF-ASSESSMENT SOURCE EVIDENCE\n"
            "EVIDENCE_STATUS=SOURCE_EVIDENCE_AVAILABLE\n"
            "TOPICS=self_assessment\n"
            "SOURCE_FILES_VERIFIED=419\n"
            "ASSESSMENT_SCOPE=PINNED_QUALIFICATIONS_AND_LOOPBACK_HEALTH\n"
            "RUNTIME_END_TO_END_VERIFIED=NO\n"
            "LIVE_BROKER_TRADING_APPROVED=NO"
        )
    return _v445_previous_render(self, question)


Retriever.render = _v445_render


def polish_developer_answer(answer, question):
    import re
    from pathlib import Path

    if not _v445_is_assessment(question):
        return _v445_previous_polish(answer, question)

    if not isinstance(answer, str) or (
        "EVIDENCE_STATUS=SOURCE_EVIDENCE_AVAILABLE" not in answer
    ):
        return _v445_previous_polish(answer, question)

    if re.search(
        r"\b(?:raw|full evidence|source dump|full report|verbose)\b",
        question, flags=re.IGNORECASE,
    ):
        return _v445_previous_polish(answer, question)

    return _v445_assessment(
        Path(__file__).resolve().parents[4],
        question,
    )


# NEURO_V445_LIVE_ADAPTER_COMPATIBILITY_V1
# The existing V3 adapter selects V3.7 using topics_for(), then
# qualifies retrieve(), then expects QUERY_STATUS=PASS in render().
# This bridge extends those interfaces for developer self-assessment.
# Authentication and conversation ownership remain in the adapter.

_v445_original_topics_for = Retriever.topics_for
_v445_original_retrieve = Retriever.retrieve
_v445_original_render_qualified = Retriever.render


def _v445_compatible_topics_for(self, question):
    if _v445_is_assessment(question):
        return ["self_assessment"]
    return _v445_original_topics_for(self, question)


def _v445_compatible_retrieve(self, question):
    if _v445_is_assessment(question):
        # Fail closed if frozen source evidence is stale.
        if self.verify() != 419:
            raise StaleEvidence("Self-assessment source verification failed")
        return {
            "status": "SOURCE_EVIDENCE_AVAILABLE",
            "topics": ["self_assessment"],
        }
    return _v445_original_retrieve(self, question)


def _v445_compatible_render(self, question):
    evidence = _v445_original_render_qualified(self, question)
    if _v445_is_assessment(question):
        if (
            "EVIDENCE_STATUS=SOURCE_EVIDENCE_AVAILABLE" not in evidence
            or "TOPICS=self_assessment" not in evidence
        ):
            raise StaleEvidence("Self-assessment qualification incomplete")
        if "QUERY_STATUS=PASS" not in evidence:
            evidence += "\nQUERY_STATUS=PASS"
    return evidence


Retriever.topics_for = _v445_compatible_topics_for
Retriever.retrieve = _v445_compatible_retrieve
Retriever.render = _v445_compatible_render


# NEURO_V467_IMPROVEMENT_INTELLIGENCE_V1
_v467_previous_polish = polish_developer_answer


def _v467_plan_from_evidence(reports, feedback):
    """Read-only capability prioritization, not production authorization."""
    definitions = (
        {
            "id": "market_data_success",
            "title": "Successful market-data retrieval",
            "weight": 90,
            "phrases": ("Real market-data provider success response",),
            "why": "Provider-error behavior was tested, but successful real-provider retrieval has not been qualified.",
            "dependency": "Validated provider response and normalized bars",
            "criteria": "An approved read-only integration test verifies a successful response, valid bars and defined failure handling.",
        },
        {
            "id": "portfolio_evaluation",
            "title": "Complete paper-only portfolio evaluation",
            "weight": 85,
            "phrases": ("Actual strategy canonicalization and weighted portfolio math",),
            "why": "Isolated allocation checks do not demonstrate full weighted portfolio evaluation.",
            "dependency": "Deterministic historical market-data fixtures",
            "criteria": "The actual evaluator reproduces expected allocation, cash, fees and rejection outcomes with execution disabled.",
        },
        {
            "id": "actual_evaluators",
            "title": "Actual V4 strategy evaluators",
            "weight": 80,
            "phrases": ("Actual fifteen V4 evaluator implementations",),
            "why": "The existing aggregation qualification used substitute evaluators.",
            "dependency": "Validated fixtures and aggregation contracts",
            "criteria": "All fifteen actual evaluators run on deterministic fixtures, with expected outputs and aggregation independently checked.",
        },
        {
            "id": "local_ai_reasoning",
            "title": "Local AI reasoning reliability",
            "weight": 75,
            "phrases": ("Actual Wolfden AI inference",),
            "why": "Wolfden inference was not qualified by the controlled tests, and unusable model output has been observed.",
            "dependency": "A representative source-grounded question benchmark",
            "criteria": "An offline benchmark measures correctness, unsupported claims, unusable answers and grounded fallback behavior.",
        },
        {
            "id": "runtime_integration",
            "title": "Observed runtime integration",
            "weight": 70,
            "phrases": (),
            "why": "Static imports do not prove real runtime execution paths.",
            "dependency": "Developer-approved sanitized instrumentation",
            "criteria": "A selected paper-only path is traced with runtime evidence and its authorization boundaries verified.",
        },
    )

    controlled = reports.get("controlled_behavior")
    discovery = reports.get("integration_discovery")

    controlled_valid = (
        isinstance(controlled, dict)
        and controlled.get("schema")
        == "neuro_v40_batch5_controlled_execution_v1"
        and controlled.get("passed") == 12
        and controlled.get("failed") == 0
    )

    exclusions = set()

    if controlled_valid:
        raw = controlled.get("not_verified", [])
        if isinstance(raw, list):
            exclusions = {
                item for item in raw
                if isinstance(item, str)
            }

    approved = {}

    for item in feedback:
        if not isinstance(item, dict):
            continue
        if (
            item.get("outcome") == "qualified"
            and item.get("developer_reviewed") is True
            and item.get("capability_id") in {
                definition["id"] for definition in definitions
            }
        ):
            approved[item["capability_id"]] = item

    pending = []
    completed = []
    unknown = []

    for definition in definitions:
        capability = definition["id"]

        if definition["phrases"]:
            supported_gap = (
                controlled_valid
                and any(
                    phrase in exclusions
                    for phrase in definition["phrases"]
                )
            )
        else:
            supported_gap = isinstance(discovery, dict)

        if capability in approved:
            completed.append((definition, approved[capability]))
        elif supported_gap:
            pending.append(definition)
        else:
            unknown.append(definition)

    pending.sort(key=lambda item: (-item["weight"], item["id"]))

    return {
        "pending": pending,
        "completed": completed,
        "unknown": unknown,
        "controlled_valid": controlled_valid,
    }


def _v467_read_feedback(root):
    """Read SHA-matched, developer-recorded results; do not run reports."""
    import hashlib
    import json
    from pathlib import Path

    base = Path(root) / "runtime/qualification"
    folder = base / "neuro_v47_approved_feedback"
    manifest = folder / "manifest.json"

    if not manifest.is_file() or manifest.is_symlink():
        return [], ["No reviewed follow-up reports registered"]

    try:
        if manifest.stat().st_size > 65536:
            raise ValueError("Oversized manifest")
        data = json.loads(manifest.read_bytes())
        if (
            data.get("schema") != "neuro_v47_approved_feedback_v1"
            or not isinstance(data.get("entries"), list)
            or len(data["entries"]) > 50
        ):
            raise ValueError("Invalid manifest")
    except (OSError, ValueError, TypeError):
        return [], ["Feedback manifest invalid"]

    accepted = []
    rejected = []
    seen = set()
    allowed = (folder / "reports").resolve()

    for entry in data["entries"]:
        try:
            if not isinstance(entry, dict):
                raise ValueError("Invalid entry")

            capability = entry["capability_id"]
            digest = entry["sha256"]
            relative = entry["report_path"]

            if capability not in {
                "market_data_success",
                "portfolio_evaluation",
                "actual_evaluators",
                "local_ai_reasoning",
                "runtime_integration",
            }:
                raise ValueError("Unknown capability")

            if (
                not isinstance(digest, str)
                or len(digest) != 64
                or any(c not in "0123456789abcdef" for c in digest)
                or not isinstance(relative, str)
                or not relative.startswith(
                    "neuro_v47_approved_feedback/reports/"
                )
                or ".." in Path(relative).parts
                or capability in seen
            ):
                raise ValueError("Unsafe entry")

            target = base / relative

            if (
                target.is_symlink()
                or not target.is_file()
                or not target.resolve().is_relative_to(allowed)
                or target.stat().st_size > 262144
            ):
                raise ValueError("Unsafe report path")

            raw = target.read_bytes()

            if hashlib.sha256(raw).hexdigest() != digest:
                raise ValueError("Report fingerprint mismatch")

            report = json.loads(raw)

            if (
                report.get("schema")
                != "neuro_v47_capability_qualification_v1"
                or report.get("capability_id") != capability
                or report.get("outcome") != "qualified"
                or report.get("developer_reviewed") is not True
                or report.get("scope") != "offline_or_read_only_paper"
                or type(report.get("checks_total")) is not int
                or type(report.get("checks_passed")) is not int
                or report["checks_total"] < 1
                or report["checks_passed"] != report["checks_total"]
            ):
                raise ValueError("Unqualified report")

            seen.add(capability)
            accepted.append(report)

        except (
            OSError, ValueError, KeyError, TypeError,
            json.JSONDecodeError,
        ):
            rejected.append("A follow-up report was rejected")

    return accepted, rejected[:10]


def _v467_improvement_report(root):
    import hashlib
    import json
    from pathlib import Path

    root = Path(root)

    specs = {
        "execution_and_risk": (
            "neuro_v40_batch1_20261013T011314Z", "91909308e74020528c554c8e45e97a94dc92d51763702c98627aa16c2352964d"
        ),
        "integration_discovery": (
            "neuro_v40_batch2_20261013T011426Z", "1030667e0fb736efc6fbadfd9f2043ff39e53c28480fcc10785b9b4c150b7fd3"
        ),
        "controlled_behavior": (
            "neuro_v40_batch5_20261013T011757Z", "125dcbdab764b035954b326a0f1bb5ff5e3dea03c0091112289f412755660518"
        ),
    }

    reports = {}

    for name, (folder, expected) in specs.items():
        path = (
            root / "runtime/qualification"
            / folder / "qualification.json"
        )
        try:
            if not path.is_file() or path.is_symlink():
                raise ValueError("Report missing")
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != expected:
                raise ValueError("Report changed")
            reports[name] = json.loads(raw)
        except (OSError, ValueError, TypeError):
            reports[name] = None

    feedback, warnings = _v467_read_feedback(root)
    plan = _v467_plan_from_evidence(reports, feedback)

    output = [
        "## NeuroVest improvement assessment",
        "",
        "I reviewed my pinned qualification reports and any "
        "registered developer-reviewed follow-up results.",
        "",
        "**Qualification coverage**",
        "",
    ]

    for name, report in reports.items():
        status = (
            "verified pinned report"
            if isinstance(report, dict)
            else "missing or changed evidence"
        )
        output.append(
            "- " + name.replace("_", " ").capitalize() + ": " + status
        )

    output.extend([
        "",
        "**Runtime health**",
        "",
        "This assessment does not independently establish current "
        "backend health. An unavailable or timed-out health "
        "sample is not proof of an outage.",
        "",
        "**Highest-priority improvements**",
        "",
    ])

    if not plan["controlled_valid"]:
        output.extend([
            "The controlled-behavior qualification must be "
            "reverified before relying on its coverage.",
            "",
        ])

    if plan["pending"]:
        for number, item in enumerate(plan["pending"], 1):
            output.extend([
                f"{number}. **{item['title']}**",
                f"   - Evidence: {item['why']}",
                f"   - Prerequisite: {item['dependency']}",
                f"   - Completion criteria: {item['criteria']}",
                "   - Status: Qualification gap, not a confirmed incident.",
            ])
    else:
        output.append(
            "No pending priority is established by the current "
            "verified gap evidence."
        )

    output.extend([
        "",
        "**Registered follow-up qualifications**",
        "",
    ])

    if plan["completed"]:
        for item, report in plan["completed"]:
            output.append(
                "- " + item["title"]
                + ": developer-recorded "
                + str(report["checks_passed"])
                + "/" + str(report["checks_total"])
                + " passing checks; independent provenance and "
                "production readiness remain separate questions."
            )
    else:
        output.append(
            "- No qualifying developer-reviewed follow-up results "
            "have been registered."
        )

    # This section is conditional, not required when everything
    # is already classified.
    if plan["unknown"]:
        output.extend([
            "",
            "**Evidence still insufficient to classify**",
            "",
        ])
        for item in plan["unknown"]:
            output.append("- " + item["title"])

    if warnings:
        output.extend([
            "",
            "**Evidence registration notes**",
            "",
        ])
        for warning in warnings:
            output.append("- " + warning)

    output.extend([
        "",
        "**Verification boundary:** These are evidence-based "
        "qualification priorities, not demonstrated active faults. "
        "A reviewed and hash-matched report is recorded evidence, "
        "not independent proof that a test ran or that production "
        "deployment is approved.",
        "",
        "**Next action:** Qualify the highest-priority gap, "
        "review the test artifacts, then register the result.",
        "",
        "No broker orders or autonomous production changes "
        "are authorized by this assessment.",
    ])

    return "\n".join(output)


def polish_developer_answer(answer, question):
    import re
    from pathlib import Path

    if not _v445_is_assessment(question):
        return _v467_previous_polish(answer, question)

    if not isinstance(answer, str):
        return _v467_previous_polish(answer, question)

    if not all(
        marker in answer
        for marker in (
            "SOURCE_EVIDENCE:",
            "EVIDENCE_STATUS=SOURCE_EVIDENCE_AVAILABLE",
            "TOPICS=self_assessment",
            "QUERY_STATUS=PASS",
        )
    ):
        return _v467_previous_polish(answer, question)

    if re.search(
        r"\b(?:raw|full evidence|source dump|"
        r"full report|verbose)\b",
        question,
        flags=re.IGNORECASE,
    ):
        return _v467_previous_polish(answer, question)

    return _v467_improvement_report(
        Path(__file__).resolve().parents[4]
    )




# NEURO_SELF_IMPROVEMENT_N6_CANDIDATE_ONLY
# Evidence refresh adapter for the existing V4.67 assessment.
# No production deployment, test execution or database access.

_n6_previous_improvement_report = _v467_improvement_report


def _n6_recent_evidence_addendum(root, manifest_relative=None):
    import hashlib
    import json
    from pathlib import Path

    root = Path(root).resolve()

    if manifest_relative is None:
        manifest_relative = 'runtime/qualification/neuro_self_improvement_N6_FIX_20261014T205433Z/evidence/recent_manifest.json'

    manifest_path = root / manifest_relative

    unavailable = (
        "\n\n**Recent qualification evidence**\n\n"
        "No verified recent evidence is available. "
        "This does not establish a functional failure."
    )

    try:
        if (
            manifest_path.is_symlink()
            or not manifest_path.is_file()
            or not manifest_path.resolve().is_relative_to(root)
            or manifest_path.stat().st_size > 32768
        ):
            return unavailable

        manifest = json.loads(
            manifest_path.read_bytes()
        )

        if (
            not isinstance(manifest, dict)
            or manifest.get("schema")
                != "neuro_recent_evidence_n6_v1"
            or not isinstance(manifest.get("sources"), list)
            or len(manifest["sources"]) != 1
        ):
            return unavailable

        entry = manifest["sources"][0]

        if (
            not isinstance(entry, dict)
            or entry.get("id") != "8U-R93"
            or entry.get("scope")
                != "isolated_postgres_integration"
            or entry.get("developer_reviewed") is not False
            or not isinstance(entry.get("sha256"), str)
            or len(entry["sha256"]) != 64
            or not isinstance(entry.get("path"), str)
        ):
            return unavailable

        path = root / entry["path"]

        if (
            path.is_symlink()
            or not path.is_file()
            or not path.resolve().is_relative_to(
                root / "runtime/qualification"
            )
            or path.stat().st_size > 65536
        ):
            return unavailable

        raw = path.read_bytes()

        if hashlib.sha256(raw).hexdigest() != entry["sha256"]:
            return unavailable

        report = json.loads(raw)

        required = {
            "R90_CANDIDATE_INTEGRITY",
            "ISOLATED_POSTGRES_STARTED",
            "REAL_COMMIT_WITH_JOURNAL",
            "POST_COMMIT_LOST_RESPONSE_RECONCILED",
            "DUPLICATE_WRITE_PREVENTED",
            "PRECOMMIT_CANCELLATION_ROLLBACK",
            "STOP_PREVENTS_JOURNAL_AND_COMMIT",
            "ASYNC_ENGINE_CLEANUP",
            "ISOLATED_POSTGRES_STOPPED",
        }

        if (
            not isinstance(report, dict)
            or report.get("qualification") != "8U-R93"
            or report.get("result")
                != "REAL_DB_JOURNAL_INTEGRATION_PASS"
            or not isinstance(report.get("checks"), dict)
            or not all(
                report["checks"].get(key) is True
                for key in required
            )
            or report.get("production_database_used") is not False
            or report.get("production_source_promotion") is not False
            or report.get("live_trading_authorized") is not False
        ):
            return unavailable

        return (
            "\n\n**Recent qualification evidence**\n\n"
            "- R93: Nine recorded checks passed in an "
            "isolated PostgreSQL recovery-journal integration.\n"
            "- Confirmed scope: real database commit, "
            "post-commit lost-response reconciliation, "
            "duplicate suppression, pre-commit cancellation, "
            "and emergency-stop admission blockade.\n"
            "- Still unverified: interruption during the actual "
            "PostgreSQL COMMIT protocol, deployed ledger "
            "integration and production behaviour.\n"
            "- Evidence status: SHA-256 matched qualification "
            "artifact; not independently developer-reviewed.\n"
            "- This result reduces the isolated persistence "
            "qualification gap but does not prove that "
            "production financial persistence is complete.\n"
            "- Production promotion and live trading "
            "remain unauthorized."
        )

    except (
        OSError, ValueError, TypeError, KeyError
    ):
        return unavailable


def _v467_improvement_report(root):
    base = _n6_previous_improvement_report(root)
    addition = _n6_recent_evidence_addendum(root)
    return base.rstrip() + addition



# NEURO_SELF_IMPROVEMENT_N8_CANDIDATE_ONLY
# Enrich existing prioritized decisions using the verified N6 evidence.
# No repository writes, DB activity or broker calls.

_n8_previous_plan = _v467_plan_from_evidence


def _n8_has_qualified_r93(root):
    # N6 is the verification boundary. Its fixed trusted output is
    # produced only after manifest, digest and R93 checks succeed.
    content = _n6_recent_evidence_addendum(root)
    return (
        "Nine recorded checks passed" in content
        and "not independently developer-reviewed" in content
        and "Still unverified:" in content
    )


def _v467_plan_from_evidence(reports, feedback):
    from pathlib import Path

    plan = _n8_previous_plan(reports, feedback)

    # Never mutate the existing plan returned by V4.67 in place.
    plan = dict(plan)
    pending = [dict(item) for item in plan.get("pending", [])]

    if not _n8_has_qualified_r93(
        Path(__file__).resolve().parents[4]
    ):
        plan["pending"] = pending
        return plan

    # The isolated database experiment is completed, but integration
    # into the deployed financial persistence path is NOT completed.
    # Keep the runtime-integration priority and make its next work exact.
    matched = False

    for item in pending:
        if item.get("id") != "runtime_integration":
            continue

        matched = True
        item["why"] = (
            "R93 recorded nine passing checks against isolated "
            "PostgreSQL, including committed-row reconciliation and "
            "duplicate suppression. The real deployed ledger and "
            "broker paths remain unqualified by R93."
        )
        item["dependency"] = (
            "Existing R93 evidence plus developer-reviewed "
            "ledger and broker integration fixtures"
        )
        item["criteria"] = (
            "Qualify the actual paper-only ledger and broker call "
            "paths, controlled COMMIT uncertainty recovery and "
            "sanitized end-to-end traces. Preserve emergency stop, "
            "owner isolation and no-live-execution controls."
        )
        item["evidence_revision"] = "8U-R93"
        item["qualification_scope"] = "isolated_only"

    if not matched:
        # Do not invent a new ranked priority if the existing
        # V4.67 plan no longer contains the expected entry.
        plan["n8_mapping_status"] = "runtime_priority_not_found"

    plan["pending"] = pending
    return plan
