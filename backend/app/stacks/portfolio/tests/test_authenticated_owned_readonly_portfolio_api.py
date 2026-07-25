from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.app.spine.L5_api.owned_readonly_portfolio_service import (
    AuthenticatedPortfolioAccessDenied,
    build_owned_facade,
    serialize_accounts,
    serialize_balances,
    serialize_overview,
    serialize_positions,
    serialize_symbol_positions,
    serialize_totals,
)


def latest_snapshot() -> Path:
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


def configured_owner() -> str:
    registry = json.loads(
        Path(
            "runtime/dev_auth/"
            "snaptrade_portfolio_owner_bindings.json"
        ).read_text(
            encoding="utf-8",
        )
    )

    bindings = registry.get(
        "bindings",
        {},
    )

    if len(
        bindings
    ) != 1:
        pytest.skip(
            "Exactly one qualification owner is required."
        )

    return next(
        iter(
            bindings
        )
    )


def test_configured_owner_receives_two_accounts() -> None:
    facade = build_owned_facade(
        neurovest_user_id=configured_owner(),
        source_path=latest_snapshot(),
    )

    overview = serialize_overview(
        facade
    )

    assert overview[
        "account_count"
    ] == 2

    assert overview[
        "balance_record_count"
    ] == 2

    assert overview[
        "position_count"
    ] == 5

    assert overview[
        "read_only"
    ] is True

    assert overview[
        "paper_only"
    ] is True

    assert overview[
        "trading_enabled"
    ] is False

    assert overview[
        "order_operations_enabled"
    ] is False


def test_unbound_user_is_denied() -> None:
    with pytest.raises(
        AuthenticatedPortfolioAccessDenied
    ):
        build_owned_facade(
            neurovest_user_id=(
                "qualification-unbound-user"
            ),
            source_path=latest_snapshot(),
        )


def test_empty_principal_subject_is_denied() -> None:
    with pytest.raises(
        AuthenticatedPortfolioAccessDenied
    ):
        build_owned_facade(
            neurovest_user_id=" ",
            source_path=latest_snapshot(),
        )


def test_owner_receives_only_bound_account_hashes() -> None:
    facade = build_owned_facade(
        neurovest_user_id=configured_owner(),
        source_path=latest_snapshot(),
    )

    registry = json.loads(
        Path(
            "runtime/dev_auth/"
            "snaptrade_portfolio_owner_bindings.json"
        ).read_text(
            encoding="utf-8",
        )
    )

    expected = set(
        registry[
            "bindings"
        ][
            configured_owner()
        ]
    )

    actual = {
        account[
            "account_id_hash"
        ]
        for account in serialize_accounts(
            facade
        )
    }

    assert actual == expected


def test_read_views_are_normalized() -> None:
    facade = build_owned_facade(
        neurovest_user_id=configured_owner(),
        source_path=latest_snapshot(),
    )

    accounts = serialize_accounts(
        facade
    )

    balances = serialize_balances(
        facade
    )

    positions = serialize_positions(
        facade
    )

    totals = serialize_totals(
        facade
    )

    assert len(
        accounts
    ) == 2

    assert len(
        balances
    ) == 2

    assert len(
        positions
    ) == 5

    assert isinstance(
        totals,
        dict,
    )

    assert all(
        len(
            account[
                "account_id_hash"
            ]
        ) == 64
        for account in accounts
    )


def test_symbol_lookup_is_owner_scoped() -> None:
    facade = build_owned_facade(
        neurovest_user_id=configured_owner(),
        source_path=latest_snapshot(),
    )

    positions = serialize_symbol_positions(
        facade,
        "aapl",
    )

    assert positions

    assert all(
        item[
            "position"
        ][
            "symbol"
        ] == "AAPL"
        for item in positions
    )


def test_no_raw_account_identifier_fields_are_returned() -> None:
    facade = build_owned_facade(
        neurovest_user_id=configured_owner(),
        source_path=latest_snapshot(),
    )

    payload = json.dumps(
        {
            "accounts":
                serialize_accounts(
                    facade
                ),
            "balances":
                serialize_balances(
                    facade
                ),
            "positions":
                serialize_positions(
                    facade
                ),
        }
    ).lower()

    forbidden = (
        '"account_number"',
        '"raw_account_id"',
        '"user_secret"',
        '"consumer_key"',
        '"client_id"',
        '"order"',
        '"trade"',
    )

    for marker in forbidden:
        assert marker not in payload


def test_service_records_no_network_or_database_activity() -> None:
    facade = build_owned_facade(
        neurovest_user_id=configured_owner(),
        source_path=latest_snapshot(),
    )

    snapshot = facade.snapshot

    assert snapshot.network_request_count == 0
    assert snapshot.database_persisted is False
    assert snapshot.trading_enabled is False
    assert snapshot.order_operations_enabled is False
