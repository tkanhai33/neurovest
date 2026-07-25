from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.app.stacks.snaptrade.application.portfolio_owner_binding import (
    PortfolioOwnerBindingError,
    PortfolioOwnerBindingNotFound,
    filter_owned_accounts,
    hash_account_identifier,
    load_portfolio_owner_binding_registry,
    resolve_owned_account_hashes,
)


def write_registry(
    tmp_path: Path,
    *,
    bindings: dict[str, list[str]],
) -> Path:
    path = (
        tmp_path
        / "owner_bindings.json"
    )

    path.write_text(
        json.dumps(
            {
                "schema":
                    "neurovest.snaptrade_portfolio_owner_bindings",
                "schema_version":
                    1,
                "bindings":
                    bindings,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    return path


def test_empty_registry_fails_closed(
    tmp_path: Path,
) -> None:
    path = write_registry(
        tmp_path,
        bindings={},
    )

    with pytest.raises(
        PortfolioOwnerBindingNotFound
    ):
        resolve_owned_account_hashes(
            neurovest_user_id="user-a",
            registry_path=path,
        )


def test_resolves_only_authenticated_owner(
    tmp_path: Path,
) -> None:
    first = hash_account_identifier(
        "account-one"
    )

    second = hash_account_identifier(
        "account-two"
    )

    path = write_registry(
        tmp_path,
        bindings={
            "user-a": [
                first,
            ],
            "user-b": [
                second,
            ],
        },
    )

    assert resolve_owned_account_hashes(
        neurovest_user_id="user-a",
        registry_path=path,
    ) == (
        first,
    )

    assert resolve_owned_account_hashes(
        neurovest_user_id="user-b",
        registry_path=path,
    ) == (
        second,
    )


def test_rejects_cross_owner_account_reuse(
    tmp_path: Path,
) -> None:
    account_hash = hash_account_identifier(
        "shared-account"
    )

    path = write_registry(
        tmp_path,
        bindings={
            "user-a": [
                account_hash,
            ],
            "user-b": [
                account_hash,
            ],
        },
    )

    with pytest.raises(
        PortfolioOwnerBindingError,
        match="multiple NeuroVest users",
    ):
        load_portfolio_owner_binding_registry(
            path
        )


def test_filters_snapshot_accounts_to_owner(
    tmp_path: Path,
) -> None:
    first = hash_account_identifier(
        "account-one"
    )

    second = hash_account_identifier(
        "account-two"
    )

    path = write_registry(
        tmp_path,
        bindings={
            "user-a": [
                first,
            ],
        },
    )

    assert filter_owned_accounts(
        neurovest_user_id="user-a",
        available_account_hashes=(
            first,
            second,
        ),
        registry_path=path,
    ) == (
        first,
    )


def test_rejects_binding_to_absent_snapshot_account(
    tmp_path: Path,
) -> None:
    owned = hash_account_identifier(
        "owned-account"
    )

    other = hash_account_identifier(
        "other-account"
    )

    path = write_registry(
        tmp_path,
        bindings={
            "user-a": [
                owned,
            ],
        },
    )

    with pytest.raises(
        PortfolioOwnerBindingError,
        match="absent",
    ):
        filter_owned_accounts(
            neurovest_user_id="user-a",
            available_account_hashes=(
                other,
            ),
            registry_path=path,
        )


@pytest.mark.parametrize(
    "user_id",
    (
        "",
        " ",
        "\t",
    ),
)
def test_rejects_empty_user_id(
    tmp_path: Path,
    user_id: str,
) -> None:
    path = write_registry(
        tmp_path,
        bindings={},
    )

    with pytest.raises(
        PortfolioOwnerBindingError,
        match="cannot be empty",
    ):
        resolve_owned_account_hashes(
            neurovest_user_id=user_id,
            registry_path=path,
        )


def test_registry_contains_no_raw_account_ids(
    tmp_path: Path,
) -> None:
    account_hash = hash_account_identifier(
        "private-account-id"
    )

    path = write_registry(
        tmp_path,
        bindings={
            "user-a": [
                account_hash,
            ],
        },
    )

    content = path.read_text(
        encoding="utf-8",
    )

    assert "private-account-id" not in content
    assert account_hash in content
