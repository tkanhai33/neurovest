
import ast
import asyncio
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from backend.app.stacks.chat_public import (
    chat_runtime,
    financial_analysis_chat_bridge as universe,
    answer_relevance_3dr2 as relevance,
    developer_authorization_3er1 as legacy,
)


def _code():
    path = Path(chat_runtime.__file__)
    tree = ast.parse(path.read_bytes())
    run = next(
        n for n in tree.body
        if isinstance(n, ast.AsyncFunctionDef)
        and n.name == "run_chat_turn"
    )
    selected = []
    recording = False
    for node in run.body:
        if isinstance(node, ast.ImportFrom) and any(
            a.asname == "_universe_reply_v2"
            for a in node.names
        ):
            recording = True
        if recording:
            selected.append(node)
            if isinstance(node, ast.If) and (
                ast.unparse(node.test) == "_nv3e_reply is not None"
            ):
                break

    assert selected
    assert (
        ast.unparse(selected[-1].test)
        == "_nv3e_reply is not None"
    )
    before = ast.parse(
        "assistant_content = answer\n"
        "runtime_result = result\n"
        "_nv5_selected = v5\n"
        "_nv_r10_evidence_selected = r10\n"
    ).body
    after = ast.parse(
        "return (assistant_content, runtime_result, "
        "_nv_qualified_developer_evidence, "
        "_nv_r10_preserve_evidence)"
    ).body
    args = ast.arguments(
        posonlyargs=[],
        args=[
            ast.arg(arg=name)
            for name in ("answer", "result", "v5", "r10")
        ],
        vararg=None,
        kwonlyargs=[],
        kw_defaults=[],
        kwarg=None,
        defaults=[],
    )
    module = ast.Module(
        body=[
            ast.AsyncFunctionDef(
                name="execute",
                args=args,
                body=before + selected + after,
                decorator_list=[],
                returns=None,
                type_comment=None,
            )
        ],
        type_ignores=[],
    )
    ast.fix_missing_locations(module)
    return compile(module, str(path), "exec")


async def _scenario(v5=False, r10=False, authorized=True):
    original = "Verified developer evidence answer"
    events = []

    def universe_reply(*a, **kw):
        events.append("universe")
        return "UNIVERSE OVERRIDE"

    async def relevance_reply(**kw):
        events.append("relevance")
        return "RELEVANCE OVERRIDE", "repaired"

    def legacy_reply(**kw):
        events.append("legacy")
        return "LEGACY OVERRIDE"

    result = {
        "status": "ok",
        "intent": "developer_architecture_awareness",
        "response": {
            "type": "text",
            "message": original,
        },
        "tool_truth_state": "grounded",
    }
    ns = {
        "request": SimpleNamespace(message="Explain chat routing"),
        "financial_chat_evidence": "",
        "_g41_network_only": False,
        "principal": SimpleNamespace(subject="developer"),
        "developer_evidence_allowed": authorized,
        "_v3_developer_role": lambda p: authorized,
    }
    with (
        patch.object(
            universe,
            "authoritative_universe_reply",
            universe_reply,
        ),
        patch.object(
            relevance, "verify_and_repair", relevance_reply,
        ),
        patch.object(
            relevance, "clean_general_reply", lambda *a, **kw: "",
        ),
        patch.object(
            legacy, "assessed_developer_reply", legacy_reply,
        ),
    ):
        exec(_code(), ns)
        content, final, protected, skipped = (
            await ns["execute"](original, result, v5, r10)
        )
    return content, final, protected, skipped, events, original


def test_v5_preserved():
    content, result, protected, skipped, events, original = (
        asyncio.run(_scenario(v5=True))
    )
    assert protected and skipped
    assert content == result["response"]["message"] == original
    assert events == ["universe"]


def test_r10_preserved():
    content, result, protected, skipped, events, original = (
        asyncio.run(_scenario(r10=True))
    )
    assert protected and skipped
    assert content == result["response"]["message"] == original
    assert events == ["universe"]


def test_normal_processing_preserved():
    content, result, protected, skipped, events, original = (
        asyncio.run(_scenario())
    )
    assert not protected and not skipped
    assert content == "LEGACY OVERRIDE"
    assert events == ["universe", "relevance", "legacy"]


def test_unauthorized_v5_marker_rejected():
    content, result, protected, skipped, events, original = (
        asyncio.run(_scenario(v5=True, authorized=False))
    )
    assert not protected and not skipped
    assert content == "LEGACY OVERRIDE"
    assert events == ["universe", "relevance", "legacy"]


def test_unauthorized_r10_marker_rejected():
    content, result, protected, skipped, events, original = (
        asyncio.run(_scenario(r10=True, authorized=False))
    )
    assert not protected and not skipped
    assert content == "LEGACY OVERRIDE"
    assert events == ["universe", "relevance", "legacy"]
