from __future__ import annotations

import json
import logging
import urllib.request

LOGGER = logging.getLogger(
    "neurovest.ollama_completion"
)

MAX_RESPONSE_BYTES = 262144
MAX_CONTINUATIONS = 1

MARKER = "NEUROVEST_COMPLETION_GUARD_3DR1"


class IncompleteGenerationError(RuntimeError):
    pass


def _content(envelope):
    if not isinstance(envelope, dict):
        raise IncompleteGenerationError(
            "invalid_ollama_envelope"
        )

    message = envelope.get("message")

    if not isinstance(message, dict):
        raise IncompleteGenerationError(
            "invalid_ollama_message"
        )

    content = message.get("content")

    if not isinstance(content, str):
        raise IncompleteGenerationError(
            "invalid_ollama_content"
        )

    return content


def _reason(envelope):
    reason = envelope.get("done_reason")

    if reason is None:
        return "unknown"

    return str(reason).lower().strip()


def _completed(envelope):
    reason = _reason(envelope)

    return (
        envelope.get("done") is True
        and reason == "stop"
    )


def _request_payload(request):
    raw = getattr(request, "data", None)

    if not isinstance(raw, bytes):
        raise IncompleteGenerationError(
            "original_request_payload_missing"
        )

    try:
        payload = json.loads(raw)
    except (ValueError, TypeError) as exc:
        raise IncompleteGenerationError(
            "invalid_original_request_payload"
        ) from exc

    if not isinstance(payload, dict):
        raise IncompleteGenerationError(
            "invalid_original_request_shape"
        )

    return payload


def _continuation_request(request, content):
    payload = _request_payload(request)

    messages = payload.get("messages")

    if not isinstance(messages, list) or not messages:
        raise IncompleteGenerationError(
            "continuation_requires_chat_messages"
        )

    if not all(
        isinstance(message, dict)
        for message in messages
    ):
        raise IncompleteGenerationError(
            "invalid_chat_messages"
        )

    if payload.get("stream") is not False:
        raise IncompleteGenerationError(
            "continuation_requires_nonstreaming"
        )

    previous = list(messages)

    previous.append({
        "role": "assistant",
        "content": content,
    })

    previous.append({
        "role": "user",
        "content": (
            "Continue your immediately preceding answer "
            "from where it stopped. Do not restart or "
            "repeat the previous text. Finish the answer "
            "naturally, concisely, and completely. "
            "Do not invent new research or tool results."
        ),
    })

    payload["messages"] = previous

    options = payload.get("options")

    if not isinstance(options, dict):
        options = {}

    else:
        options = dict(options)

    existing_limit = options.get("num_predict")

    if (
        type(existing_limit) is int
        and existing_limit > 0
    ):
        limit = min(
            max(existing_limit, 512),
            1024,
        )
    else:
        limit = 512

    options["num_predict"] = limit

    payload["options"] = options
    payload["stream"] = False

    body = json.dumps(
        payload,
        ensure_ascii=False,
    ).encode("utf-8")

    return urllib.request.Request(
        request.full_url,
        data=body,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )


def finish_response(
    *,
    request,
    envelope,
    timeout,
):
    """
    Validates Ollama /api/chat completion metadata.

    Existing normal completed answers are unchanged.

    If the model exhausts its generation allowance,
    perform at most one bounded continuation.

    If completion cannot be verified, fail instead
    of presenting a partial response as complete.
    The existing caller's fallback path remains
    responsible for recovery.
    """
    first_content = _content(envelope)
    first_reason = _reason(envelope)

    LOGGER.info(
        "ollama_completion initial_reason=%s "
        "done=%s content_chars=%s",
        first_reason,
        envelope.get("done"),
        len(first_content),
    )

    # Older Ollama deployments might omit reason.
    # Preserve their legacy behavior, but log that
    # completion was not independently established.
    if first_reason == "unknown":
        LOGGER.warning(
            "ollama_completion reason_unavailable"
        )
        return (
            first_content.strip()
            or "Neuro online."
        )

    if _completed(envelope):
        return (
            first_content.strip()
            or "Neuro online."
        )

    if first_reason != "length":
        raise IncompleteGenerationError(
            "generation_not_verified_complete:"
            + first_reason
        )

    if not first_content.strip():
        raise IncompleteGenerationError(
            "length_limit_with_empty_output"
        )

    LOGGER.warning(
        "ollama_completion length_limit_detected "
        "attempting_bounded_continuation"
    )

    if MAX_CONTINUATIONS < 1:
        raise IncompleteGenerationError(
            "continuation_disabled"
        )

    continuation_request = _continuation_request(
        request,
        first_content,
    )

    try:
        with urllib.request.urlopen(
            continuation_request,
            timeout=timeout,
        ) as response:
            raw = response.read(
                MAX_RESPONSE_BYTES + 1
            )

        if len(raw) > MAX_RESPONSE_BYTES:
            raise IncompleteGenerationError(
                "continuation_response_too_large"
            )

        continued = json.loads(raw)

    except (
        OSError,
        ValueError,
        TypeError,
    ) as exc:
        raise IncompleteGenerationError(
            "continuation_request_failed"
        ) from exc

    if not _completed(continued):
        LOGGER.warning(
            "ollama_completion continuation_incomplete "
            "reason=%s",
            _reason(continued),
        )

        raise IncompleteGenerationError(
            "continuation_not_complete"
        )

    continuation_text = _content(continued)

    if not continuation_text.strip():
        raise IncompleteGenerationError(
            "continuation_empty"
        )

    LOGGER.info(
        "ollama_completion continuation_success "
        "additional_chars=%s",
        len(continuation_text),
    )

    # The model has been instructed not to repeat
    # earlier text. This combines generated content,
    # not an invented completion.
    return (
        first_content.rstrip()
        + "\n"
        + continuation_text.lstrip()
    ).strip()
