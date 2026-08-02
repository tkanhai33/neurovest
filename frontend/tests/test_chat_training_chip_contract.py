from pathlib import Path


SERVICE = Path(
    "frontend/services/chatService.ts"
)

WIDGET = Path(
    "frontend/app/components/chat/"
    "FloatingChatWidget.tsx"
)

ROUTE = Path(
    "frontend/app/api/v1/training/"
    "runs/[run_id]/route.ts"
)


def test_chat_message_preserves_training_run() -> None:
    source = SERVICE.read_text(
        encoding="utf-8",
    )

    assert (
        "export type TrainingRunSummary"
        in source
    )

    assert (
        "trainingRun?: TrainingRunSummary | null"
        in source
    )

    assert (
        "training_run?:"
        in source
    )

    assert (
        "normalizeTrainingRun("
        in source
    )


def test_training_status_client_is_owner_scoped() -> None:
    source = SERVICE.read_text(
        encoding="utf-8",
    )

    assert (
        "export async function getTrainingRun("
        in source
    )

    assert (
        "`/api/v1/training/runs/${encodeURIComponent("
        in source
    )

    assert (
        'credentials: "include"'
        in source
    )


def test_floating_widget_renders_training_chip() -> None:
    source = WIDGET.read_text(
        encoding="utf-8",
    )

    assert (
        'data-testid="chat-training-chip"'
        in source
    )

    assert (
        "Training active"
        in source
    )

    assert (
        "Training complete"
        in source
    )

    assert (
        "progress_percent"
        in source
    )

    assert (
        "eligible_symbol_count"
        in source
    )

    assert (
        "rows_evaluated"
        in source
    )


def test_floating_widget_polls_and_stops_terminal_runs() -> None:
    source = WIDGET.read_text(
        encoding="utf-8",
    )

    assert (
        "window.setInterval("
        in source
    )

    assert (
        "await getTrainingRun("
        in source
    )

    for status in (
        '"completed"',
        '"failed"',
        '"cancelled"',
        '"canceled"',
    ):
        assert status in source


def test_training_proxy_uses_authenticated_backend_fetch() -> None:
    source = ROUTE.read_text(
        encoding="utf-8",
    )

    assert (
        "backendFetch"
        in source
    )

    assert (
        "`/api/v1/training/runs/${encodeURIComponent("
        in source
    )

    assert (
        '"Cache-Control"'
        in source
    )


def test_public_chip_does_not_reference_internal_ownership() -> None:
    combined = "\n".join(
        path.read_text(
            encoding="utf-8",
        )
        for path in (
            SERVICE,
            WIDGET,
            ROUTE,
        )
    )

    forbidden = (
        "owner_user_id",
        "owner_session_id",
        "requested_by_role",
        "sanitized_learning_contribution",
    )

    for value in forbidden:
        assert value not in combined
