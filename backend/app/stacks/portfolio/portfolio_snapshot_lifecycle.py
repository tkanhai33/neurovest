from __future__ import annotations

import fcntl
import hashlib
import json
import os
import tempfile
from contextlib import contextmanager
from dataclasses import asdict
from decimal import Decimal
from datetime import (
    UTC,
    datetime,
    timedelta,
)
from pathlib import Path
from typing import Any, Iterator

from backend.app.spine.L5_api.owned_readonly_portfolio_service import (
    AuthenticatedPortfolioAccessDenied,
    build_owned_snapshot,
    find_latest_normalized_portfolio,
)

from backend.app.spine.L5_api.owned_readonly_portfolio_service import (
    AuthenticatedPortfolioUnavailable,
)


ROOT = Path(".").resolve()

DEFAULT_RUNTIME_ROOT = (
    ROOT
    / "runtime"
    / "snaptrade_portfolio_lifecycle"
)

DEFAULT_STALE_AFTER = timedelta(
    minutes=15,
)

DEFAULT_RETENTION_COUNT = 5


class PortfolioSnapshotLifecycleError(
    RuntimeError
):
    pass


class PortfolioRefreshInProgress(
    PortfolioSnapshotLifecycleError
):
    pass


def utc_now() -> datetime:
    return datetime.now(
        UTC
    )


def owner_hash(
    neurovest_user_id: str,
) -> str:
    normalized = str(
        neurovest_user_id
    ).strip()

    if not normalized:
        raise AuthenticatedPortfolioAccessDenied(
            "Authenticated principal subject is missing."
        )

    return hashlib.sha256(
        normalized.encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as source:
        for chunk in iter(
            lambda:
                source.read(
                    1024 * 1024
                ),
            b"",
        ):
            digest.update(
                chunk
            )

    return digest.hexdigest()


def _json_default(
    value: Any,
) -> Any:
    if isinstance(
        value,
        Decimal,
    ):
        return format(
            value,
            "f",
        )

    if isinstance(
        value,
        (
            tuple,
            set,
        ),
    ):
        return list(
            value
        )

    if isinstance(
        value,
        Path,
    ):
        return str(
            value
        )

    if isinstance(
        value,
        datetime,
    ):
        return value.isoformat()

    raise TypeError(
        "Object of type "
        f"{type(value).__name__} "
        "is not JSON serializable"
    )


def atomic_write_json(
    destination: Path,
    payload: dict[str, Any],
) -> None:
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    serialized = (
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            default=_json_default,
        )
        + "\n"
    )

    temporary_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=destination.parent,
            prefix=(
                destination.name
                + "."
            ),
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary.write(
                serialized
            )

            temporary.flush()

            os.fsync(
                temporary.fileno()
            )

            temporary_path = Path(
                temporary.name
            )

        os.replace(
            temporary_path,
            destination,
        )

        directory_fd = os.open(
            destination.parent,
            os.O_DIRECTORY,
        )

        try:
            os.fsync(
                directory_fd
            )
        finally:
            os.close(
                directory_fd
            )
    finally:
        if (
            temporary_path is not None
            and temporary_path.exists()
        ):
            temporary_path.unlink(
                missing_ok=True
            )


@contextmanager
def owner_refresh_lock(
    owner_directory: Path,
) -> Iterator[None]:
    owner_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    lock_path = (
        owner_directory
        / "refresh.lock"
    )

    with lock_path.open(
        "a+",
        encoding="utf-8",
    ) as lock_file:
        try:
            fcntl.flock(
                lock_file.fileno(),
                (
                    fcntl.LOCK_EX
                    | fcntl.LOCK_NB
                ),
            )
        except BlockingIOError as error:
            raise PortfolioRefreshInProgress(
                "A portfolio refresh is already active for this user."
            ) from error

        try:
            yield
        finally:
            fcntl.flock(
                lock_file.fileno(),
                fcntl.LOCK_UN,
            )


def _owner_directory(
    neurovest_user_id: str,
    runtime_root: Path,
) -> Path:
    return (
        runtime_root
        / owner_hash(
            neurovest_user_id
        )
    )


def _metadata_path(
    owner_directory: Path,
) -> Path:
    return (
        owner_directory
        / "lifecycle.json"
    )


def _active_path(
    owner_directory: Path,
) -> Path:
    return (
        owner_directory
        / "active.json"
    )


def _history_directory(
    owner_directory: Path,
) -> Path:
    return (
        owner_directory
        / "history"
    )


def _read_json(
    path: Path,
) -> dict[str, Any] | None:
    if not path.is_file():
        return None

    try:
        payload = json.loads(
            path.read_text(
                encoding="utf-8",
            )
        )
    except Exception:
        return None

    return (
        payload
        if isinstance(
            payload,
            dict,
        )
        else None
    )


def _freshness(
    *,
    promoted_at: datetime | None,
    now: datetime,
    stale_after: timedelta,
) -> tuple[
    str,
    int | None,
    str | None,
]:
    if promoted_at is None:
        return (
            "missing",
            None,
            None,
        )

    age_seconds = max(
        0,
        int(
            (
                now
                - promoted_at
            ).total_seconds()
        ),
    )

    stale_at = (
        promoted_at
        + stale_after
    )

    state = (
        "fresh"
        if now < stale_at
        else "stale"
    )

    return (
        state,
        age_seconds,
        stale_at.isoformat(),
    )


def get_portfolio_lifecycle(
    *,
    neurovest_user_id: str,
    runtime_root: Path = (
        DEFAULT_RUNTIME_ROOT
    ),
    stale_after: timedelta = (
        DEFAULT_STALE_AFTER
    ),
    now: datetime | None = None,
) -> dict[str, Any]:
    current_time = (
        now
        if now is not None
        else utc_now()
    )

    owner_directory = _owner_directory(
        neurovest_user_id,
        runtime_root,
    )

    metadata = (
        _read_json(
            _metadata_path(
                owner_directory
            )
        )
        or {}
    )

    active_path = _active_path(
        owner_directory
    )

    promoted_at: datetime | None = None

    promoted_text = metadata.get(
        "last_successful_refresh_at"
    )

    if isinstance(
        promoted_text,
        str,
    ):
        try:
            promoted_at = datetime.fromisoformat(
                promoted_text
            )

            if promoted_at.tzinfo is None:
                promoted_at = promoted_at.replace(
                    tzinfo=UTC
                )

            promoted_at = promoted_at.astimezone(
                UTC
            )
        except ValueError:
            promoted_at = None

    state, age_seconds, stale_at = (
        _freshness(
            promoted_at=promoted_at,
            now=current_time,
            stale_after=stale_after,
        )
    )

    history_directory = _history_directory(
        owner_directory
    )

    history_count = (
        len(
            list(
                history_directory.glob(
                    "*.json"
                )
            )
        )
        if history_directory.is_dir()
        else 0
    )

    result = {
        "status":
            "ok",
        "owner_scoped":
            True,
        "read_only":
            True,
        "paper_only":
            True,
        "trading_enabled":
            False,
        "order_operations_enabled":
            False,
        "external_refresh_enabled":
            False,
        "refresh_source":
            (
                "qualified_local_snapshot_revalidation"
            ),
        "snapshot_state":
            state,
        "active_snapshot_present":
            active_path.is_file(),
        "active_snapshot_sha256":
            (
                sha256_file(
                    active_path
                )
                if active_path.is_file()
                else None
            ),
        "snapshot_age_seconds":
            age_seconds,
        "stale_after_seconds":
            int(
                stale_after.total_seconds()
            ),
        "stale_at":
            stale_at,
        "last_refresh_started_at":
            metadata.get(
                "last_refresh_started_at"
            ),
        "last_successful_refresh_at":
            metadata.get(
                "last_successful_refresh_at"
            ),
        "last_failed_refresh_at":
            metadata.get(
                "last_failed_refresh_at"
            ),
        "last_refresh_status":
            metadata.get(
                "last_refresh_status",
                "never",
            ),
        "last_failure_type":
            metadata.get(
                "last_failure_type"
            ),
        "last_failure_message":
            metadata.get(
                "last_failure_message"
            ),
        "refresh_count":
            int(
                metadata.get(
                    "refresh_count",
                    0,
                )
                or 0
            ),
        "failed_refresh_count":
            int(
                metadata.get(
                    "failed_refresh_count",
                    0,
                )
                or 0
            ),
        "retained_snapshot_count":
            history_count,
        "retention_limit":
            DEFAULT_RETENTION_COUNT,
        "network_request_count":
            0,
        "database_write_count":
            0,
    }

    return result


def _retain_history(
    history_directory: Path,
    *,
    retention_count: int,
) -> None:
    history_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    snapshots = sorted(
        history_directory.glob(
            "*.json"
        ),
        key=lambda path:
            path.stat().st_mtime,
        reverse=True,
    )

    for path in snapshots[
        retention_count:
    ]:
        path.unlink(
            missing_ok=True
        )


def refresh_portfolio_snapshot(
    *,
    neurovest_user_id: str,
    source_path: Path | str | None = None,
    runtime_root: Path = (
        DEFAULT_RUNTIME_ROOT
    ),
    retention_count: int = (
        DEFAULT_RETENTION_COUNT
    ),
    now: datetime | None = None,
) -> dict[str, Any]:
    current_time = (
        now
        if now is not None
        else utc_now()
    )

    owner_directory = _owner_directory(
        neurovest_user_id,
        runtime_root,
    )

    metadata_path = _metadata_path(
        owner_directory
    )

    active_path = _active_path(
        owner_directory
    )

    history_directory = _history_directory(
        owner_directory
    )

    with owner_refresh_lock(
        owner_directory
    ):
        metadata = (
            _read_json(
                metadata_path
            )
            or {}
        )

        started_at = current_time.isoformat()

        metadata.update(
            {
                "schema":
                    "neurovest.portfolio_snapshot_lifecycle",
                "schema_version":
                    1,
                "owner_id_sha256":
                    owner_hash(
                        neurovest_user_id
                    ),
                "last_refresh_started_at":
                    started_at,
                "last_refresh_status":
                    "running",
                "external_refresh_enabled":
                    False,
                "refresh_source":
                    (
                        "qualified_local_snapshot_revalidation"
                    ),
                "read_only":
                    True,
                "paper_only":
                    True,
                "trading_enabled":
                    False,
                "order_operations_enabled":
                    False,
                "network_request_count":
                    0,
                "database_write_count":
                    0,
            }
        )

        atomic_write_json(
            metadata_path,
            metadata,
        )

        try:
            qualified_source = (
                Path(
                    source_path
                )
                if source_path is not None
                else find_latest_normalized_portfolio()
            )

            if not qualified_source.is_file():
                raise PortfolioSnapshotLifecycleError(
                    "Qualified normalized portfolio snapshot is missing."
                )

            snapshot = build_owned_snapshot(
                neurovest_user_id=(
                    neurovest_user_id
                ),
                source_path=(
                    qualified_source
                ),
            )

            candidate = {
                "schema":
                    "neurovest.owner_scoped_portfolio_snapshot",
                "schema_version":
                    1,
                "owner_id_sha256":
                    owner_hash(
                        neurovest_user_id
                    ),
                "generated_at":
                    current_time.isoformat(),
                "source_path_sha256":
                    hashlib.sha256(
                        str(
                            qualified_source
                        ).encode(
                            "utf-8"
                        )
                    ).hexdigest(),
                "source_file_sha256":
                    sha256_file(
                        qualified_source
                    ),
                "refresh_source":
                    (
                        "qualified_local_snapshot_revalidation"
                    ),
                "external_refresh_enabled":
                    False,
                "read_only":
                    True,
                "paper_only":
                    True,
                "trading_enabled":
                    False,
                "order_operations_enabled":
                    False,
                "network_request_count":
                    0,
                "database_write_count":
                    0,
                "snapshot":
                    asdict(
                        snapshot
                    ),
            }

            if candidate[
                "snapshot"
            ].get(
                "account_count",
                0,
            ) <= 0:
                raise PortfolioSnapshotLifecycleError(
                    "Candidate snapshot contains no owned accounts."
                )

            if active_path.is_file():
                previous_timestamp = (
                    current_time.strftime(
                        "%Y%m%dT%H%M%S_%fZ"
                    )
                )

                previous_path = (
                    history_directory
                    / (
                        previous_timestamp
                        + "_last_known_good.json"
                    )
                )

                previous_payload = json.loads(
                    active_path.read_text(
                        encoding="utf-8",
                    )
                )

                atomic_write_json(
                    previous_path,
                    previous_payload,
                )

            atomic_write_json(
                active_path,
                candidate,
            )

            _retain_history(
                history_directory,
                retention_count=(
                    max(
                        1,
                        int(
                            retention_count
                        ),
                    )
                ),
            )

            refreshed_metadata = (
                _read_json(
                    metadata_path
                )
                or metadata
            )

            refreshed_metadata.update(
                {
                    "last_refresh_status":
                        "succeeded",
                    "last_successful_refresh_at":
                        current_time.isoformat(),
                    "last_failure_type":
                        None,
                    "last_failure_message":
                        None,
                    "active_snapshot_sha256":
                        sha256_file(
                            active_path
                        ),
                    "refresh_count":
                        (
                            int(
                                refreshed_metadata.get(
                                    "refresh_count",
                                    0,
                                )
                                or 0
                            )
                            + 1
                        ),
                }
            )

            atomic_write_json(
                metadata_path,
                refreshed_metadata,
            )

        except Exception as error:
            failed_metadata = (
                _read_json(
                    metadata_path
                )
                or metadata
            )

            failed_metadata.update(
                {
                    "last_refresh_status":
                        "failed",
                    "last_failed_refresh_at":
                        current_time.isoformat(),
                    "last_failure_type":
                        type(
                            error
                        ).__name__,
                    "last_failure_message":
                        str(
                            error
                        )[:500],
                    "failed_refresh_count":
                        (
                            int(
                                failed_metadata.get(
                                    "failed_refresh_count",
                                    0,
                                )
                                or 0
                            )
                            + 1
                        ),
                }
            )

            atomic_write_json(
                metadata_path,
                failed_metadata,
            )

            if isinstance(
                error,
                AuthenticatedPortfolioUnavailable,
            ):
                raise PortfolioSnapshotLifecycleError(
                    str(error)
                ) from error

            raise

    lifecycle = get_portfolio_lifecycle(
        neurovest_user_id=(
            neurovest_user_id
        ),
        runtime_root=runtime_root,
        now=current_time,
    )

    return {
        **lifecycle,
        "refresh_result":
            "succeeded",
    }


def load_active_owner_snapshot(
    *,
    neurovest_user_id: str,
    runtime_root: Path = (
        DEFAULT_RUNTIME_ROOT
    ),
) -> dict[str, Any]:
    active_path = _active_path(
        _owner_directory(
            neurovest_user_id,
            runtime_root,
        )
    )

    payload = _read_json(
        active_path
    )

    if payload is None:
        raise PortfolioSnapshotLifecycleError(
            "No active owner-scoped portfolio snapshot exists."
        )

    return payload
