
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

TOPICS = {
    "memory": {
        "terms": ("memory", "history", "conversation", "stored"),
        "functions": (
            "load_context_bundle",
            "list_messages",
            "get_conversation_state",
            "append_message",
            "upsert_conversation_state",
        ),
        "models": (
            "ChatThreadRecord",
            "ChatMessageRecord",
            "ConversationStateRecord",
            "MemoryFactRecord",
        ),
        "purpose": (
            "Separating message history, conversation state, "
            "and memory records can support different retention "
            "and retrieval requirements."
        ),
        "impact": (
            "Potentially affected operations include writing "
            "messages, recovering conversation state, and "
            "assembling future model context."
        ),
    },
    "context": {
        "terms": ("context", "prompt", "assembler", "retrieval"),
        "functions": (
            "assemble_chat_context",
            "load_context_bundle",
            "list_messages",
            "get_conversation_state",
        ),
        "models": (
            "ChatMessageRecord",
            "ConversationStateRecord",
        ),
        "purpose": (
            "A context assembly boundary can separate the "
            "information available to a model from the "
            "underlying persistent conversation records."
        ),
        "impact": (
            "Changing context assembly could affect which "
            "messages enter a prompt, their relevance, "
            "and the model's available conversational history."
        ),
    },
    "response": {
        "terms": ("response", "verification", "model", "ollama"),
        "functions": (
            "run_chat_turn",
            "handle_chat_message",
            "ask_ollama",
            "append_message",
        ),
        "models": ("ChatMessageRecord",),
        "purpose": (
            "Response verification and persistence can provide "
            "separate boundaries for checking output and "
            "retaining conversation history."
        ),
        "impact": (
            "Changes may affect response generation, "
            "verification, recorded messages, and "
            "downstream consumers."
        ),
    },
}

class EvidenceError(RuntimeError):
    pass

def load_evidence(root, evidence_path):
    root = Path(root).resolve()
    path = Path(evidence_path).resolve()
    if not path.is_file():
        raise EvidenceError("Missing evidence")

    data = json.loads(path.read_text("utf-8"))
    if data.get("schema") != (
        "neuro_awareness_v3r2_session_lineage_candidates"
    ):
        raise EvidenceError("Unexpected schema")

    for relative, expected in data["sources"].items():
        source = (root / relative).resolve()
        if not source.is_relative_to(root) or not source.is_file():
            raise EvidenceError("Unsafe or missing indexed source")
        if hashlib.sha256(source.read_bytes()).hexdigest() != expected:
            raise EvidenceError("Indexed source is stale")

    return data

class ExplanationSession:
    def __init__(self, root, evidence_path):
        self.root = Path(root).resolve()
        self.evidence_path = Path(evidence_path)
        self.subject = None

    def reply(self, question):
        data = load_evidence(self.root, self.evidence_path)
        normalized = " ".join(question.lower().split())

        if not normalized:
            return "Please ask an architecture question."

        explicit = [
            (topic, sum(term in normalized for term in config["terms"]))
            for topic, config in TOPICS.items()
        ]

        topic, score = max(explicit, key=lambda pair: pair[1])

        if score == 0:
            if self.subject is None:
                return (
                    "Which area should I explain: conversation memory, "
                    "context assembly, or response generation?"
                )
            topic = self.subject

        self.subject = topic
        config = TOPICS[topic]

        if re.search(r"\b(why|purpose|reason|designed)\b", normalized):
            mode = "WHY"
        elif re.search(r"\b(where|stored|database|table)\b", normalized):
            mode = "WHERE"
        elif re.search(
            r"\b(change|changed|impact|break|improve|alternative)\b",
            normalized,
        ):
            mode = "IMPACT"
        else:
            mode = "HOW"

        functions = {
            item["name"]: item
            for item in data["functions"]
            if item["name"] in config["functions"]
        }
        models = {
            item["class"]: item
            for item in data["models"]
            if item["class"] in config["models"]
        }

        if not functions:
            return "Evidence unavailable for this subject."

        lines = [
            "NEURO ARCHITECTURE EXPLANATION — EXPERIMENTAL",
            f"SUBJECT={topic}",
            f"QUESTION_TYPE={mode}",
            "EVIDENCE_FRESHNESS=PASS",
            "",
        ]

        if mode == "HOW":
            lines.append("HOW — OBSERVED SOURCE EVIDENCE")
            for name in config["functions"]:
                fn = functions.get(name)
                if not fn:
                    continue
                lines.append(
                    f"- {name}() is defined at "
                    f"{fn['file']}:{fn['line']}."
                )
                interesting = [
                    call for call in fn["calls_of_interest"]
                    if any(
                        token in call["call"].lower()
                        for token in (
                            "session.", "conversation_store.",
                            "self.list_messages",
                            "self.get_conversation_state",
                            "verify_response", "ask_ollama",
                        )
                    )
                ]
                for call in sorted(
                    interesting, key=lambda item: item["line"]
                )[:4]:
                    lines.append(
                        f"  Observed call: {call['call']} "
                        f"at {fn['file']}:{call['line']}"
                    )

        elif mode == "WHERE":
            lines.append("WHERE — DECLARED PERSISTENCE MODELS")
            for name in config["models"]:
                model = models.get(name)
                if model:
                    lines.append(
                        f"- {name} declares table "
                        f"{model['table']} at "
                        f"{model['lineage_file']}:{model['line']}."
                        if "lineage_file" in model else
                        f"- {name} declares table "
                        f"{model['table']} at "
                        f"backend/app/stacks/chat_public/"
                        f"persistence/chat_models.py:{model['line']}."
                    )
            lines.append(
                "These are source declarations, not confirmation "
                "of deployed schema or actual stored records."
            )

        elif mode == "WHY":
            lines.extend([
                "WHY — ARCHITECTURAL INFERENCE",
                config["purpose"],
                "This is a plausible design rationale, not "
                "a confirmed statement from the original developer.",
                "",
                "SUPPORTING EVIDENCE",
            ])
            for name in config["functions"]:
                fn = functions.get(name)
                if fn:
                    lines.append(
                        f"- {name}: {fn['file']}:{fn['line']}"
                    )

        else:
            lines.extend([
                "IMPACT — HYPOTHESIS FOR REVIEW",
                config["impact"],
                "",
                "RECOMMENDED CHECKS",
                "- Inspect direct callers and dependent tests.",
                "- Verify authorization and owner isolation.",
                "- Measure behavior before and after in simulation.",
                "- Make a reversible change only after approval.",
            ])
            for name in config["functions"]:
                fn = functions.get(name)
                if fn:
                    lines.append(
                        f"- Relevant source: {fn['file']}:{fn['line']}"
                    )

        lines.extend([
            "",
            "EVIDENCE_CLASS=STATIC_SOURCE_ANALYSIS",
            "DESIGN_INTENT_VERIFIED=NO",
            "RUNTIME_EXECUTION_VERIFIED=NO",
            "DATABASE_RECORDS_ACCESSED=NO",
            "SELF_MODIFICATION_ENABLED=NO",
            "QUERY_STATUS=PASS",
        ])

        return "\n".join(lines)
