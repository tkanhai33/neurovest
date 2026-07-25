from __future__ import annotations

import json
from datetime import (
    UTC,
    datetime,
    timedelta,
)
from pathlib import Path

import pytest

from backend.app.stacks.portfolio.portfolio_snapshot_lifecycle import (
    PortfolioSnapshotLifecycleError,
    get_portfolio_lifecycle,
    load_active_owner_snapshot,
    refresh_portfolio_snapshot,
)


OWNER_REGISTRY = Path(
    "runtime/dev_auth/"
    "snaptrade_portfolio_owner_bindings.json"
)


def configured_owner() -> str:
    document = json.loads(
        OWNER_REGISTRY.read_text(
            encoding="utf-8",
        )
    )

    bindings = document.get(
        "bindings",
        {},
    )

    if len(
        bindings
    ) != 1:
        pytest.skip(
            "Exactly one qualified owner is required."
        )

    return next(
        iter(
            bindings
        )
    )


def latest_qualified_snapshot() -> Path:
    candidates = sorted(
        Path(
            "runtime/snaptrade_integration"
        ).glob(
            (
                "portfolio_normalization_*/"
                "neurovest_snaptrade_portfolio_normalized.json"
            )
        ),
        key=lambda path:
            path.stat().st_mtime,
    )

    if not candidates:
        pytest.skip(
            "No qualified normalized portfolio exists."
        )

    return candidates[-1]


def test_refresh_promotes_owner_scoped_snapshot_atomically(
    tmp_path: Path,
) -> None:
    result = refresh_portfolio_snapshot(
        neurovest_user_id=configured_owner(),
        source_path=latest_qualified_snapshot(),
        runtime_root=tmp_path,
    )

    assert result[
        "refresh_result"
    ] == "succeeded"

    assert result[
        "snapshot_state"
    ] == "fresh"

    assert result[
        "active_snapshot_present"
    ] is True

    active = load_active_owner_snapshot(
        neurovest_user_id=configured_owner(),
        runtime_root=tmp_path,
    )

    assert active[
        "owner_id_sha256"
    ]

    assert active[
        "read_only"
    ] is True

    assert active[
        "paper_only"
    ] is True

    assert active[
        "trading_enabled"
    ] is False

    assert active[
        "order_operations_enabled"
    ] is False

    assert active[
        "network_request_count"
    ] == 0

    assert active[
        "database_write_count"
    ] == 0

    assert active[
        "snapshot"
    ][
        "account_count"
    ] == 2


def test_second_refresh_preserves_last_known_good(
    tmp_path: Path,
) -> None:
    owner = configured_owner()

    refresh_portfolio_snapshot(
        neurovest_user_id=owner,
        source_path=latest_qualified_snapshot(),
        runtime_root=tmp_path,
    )

    refresh_portfolio_snapshot(
        neurovest_user_id=owner,
        source_path=latest_qualified_snapshot(),
        runtime_root=tmp_path,
    )

    owner_directories = [
        path
        for path in tmp_path.iterdir()
        if path.is_dir()
    ]

    assert len(
        owner_directories
    ) == 1

    history = list(
        (
            owner_directories[0]
            / "history"
        ).glob(
            "*.json"
        )
    )

    assert len(
        history
    ) == 1


def test_failed_refresh_keeps_active_snapshot(
    tmp_path: Path,
) -> None:
    owner = configured_owner()

    refresh_portfolio_snapshot(
        neurovest_user_id=owner,
        source_path=latest_qualified_snapshot(),
        runtime_root=tmp_path,
    )

    before = load_active_owner_snapshot(
        neurovest_user_id=owner,
        runtime_root=tmp_path,
    )

    with pytest.raises(
        PortfolioSnapshotLifecycleError
    ):
        refresh_portfolio_snapshot(
            neurovest_user_id=owner,
            source_path=(
                tmp_path
                / "missing.json"
            ),
            runtime_root=tmp_path,
        )

    after = load_active_owner_snapshot(
        neurovest_user_id=owner,
        runtime_root=tmp_path,
    )

    assert after == before

    lifecycle = get_portfolio_lifecycle(
        neurovest_user_id=owner,
        runtime_root=tmp_path,
    )

    assert lifecycle[
        "last_refresh_status"
    ] == "failed"

    assert lifecycle[
        "active_snapshot_present"
    ] is True

    assert lifecycle[
        "failed_refresh_count"
    ] == 1


def test_staleness_is_reported(
    tmp_path: Path,
) -> None:
    owner = configured_owner()

    promoted_at = datetime(
        2026,
        7,
        24,
        12,
        0,
        tzinfo=UTC,
    )

    refresh_portfolio_snapshot(
        neurovest_user_id=owner,
        source_path=latest_qualified_snapshot(),
        runtime_root=tmp_path,
        now=promoted_at,
    )

    lifecycle = get_portfolio_lifecycle(
        neurovest_user_id=owner,
        runtime_root=tmp_path,
        stale_after=timedelta(
            minutes=15
        ),
        now=(
            promoted_at
            + timedelta(
                minutes=16
            )
        ),
    )

    assert lifecycle[
        "snapshot_state"
    ] == "stale"

    assert lifecycle[
        "snapshot_age_seconds"
    ] == 960


def test_retention_is_bounded(
    tmp_path: Path,
) -> None:
    owner = configured_owner()
    start = datetime(
        2026,
        7,
        24,
        12,
        0,
        tzinfo=UTC,
    )

    for index in range(
        9
    ):
        refresh_portfolio_snapshot(
            neurovest_user_id=owner,
            source_path=latest_qualified_snapshot(),
            runtime_root=tmp_path,
            retention_count=5,
            now=(
                start
                + timedelta(
                    seconds=index
                )
            ),
        )

    lifecycle = get_portfolio_lifecycle(
        neurovest_user_id=owner,
        runtime_root=tmp_path,
    )

    assert lifecycle[
        "retained_snapshot_count"
    ] == 5


def test_unbound_user_refresh_is_denied(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        PermissionError
    ):
        refresh_portfolio_snapshot(
            neurovest_user_id=(
                "qualification-unbound-user"
            ),
            source_path=latest_qualified_snapshot(),
            runtime_root=tmp_path,
        )


def test_lifecycle_contains_no_raw_owner_id(
    tmp_path: Path,
) -> None:
    owner = configured_owner()

    refresh_portfolio_snapshot(
        neurovest_user_id=owner,
        source_path=latest_qualified_snapshot(),
        runtime_root=tmp_path,
    )

    rendered = json.dumps(
        get_portfolio_lifecycle(
            neurovest_user_id=owner,
            runtime_root=tmp_path,
        )
    )

    assert owner not in rendered
