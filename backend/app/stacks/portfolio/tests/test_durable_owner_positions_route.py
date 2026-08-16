from __future__ import annotations

from types import SimpleNamespace

import pytest

from backend.app import main


@pytest.mark.asyncio
async def test_readonly_positions_uses_authenticated_durable_owner_service(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    principal = SimpleNamespace(
        subject="owner-123",
    )

    calls = []


    async def fake_positions_service(
        supplied_principal,
    ):

        calls.append(
            supplied_principal
        )

        return {
            "positions": [
                {
                    "symbol":
                        "TD.TO",

                    "shares_quantity":
                        "1.2500000000000000000000000000",

                    "average_entry_price":
                        "100.0000000000000000000000000000",
                },
            ],
        }


    monkeypatch.setattr(
        main,
        "get_portfolio_positions_for_api",
        fake_positions_service,
    )


    result = await (
        main.authenticated_owned_portfolio_positions(
            principal=principal,
        )
    )


    assert calls == [
        principal
    ]

    assert result[
        "status"
    ] == "ok"

    assert result[
        "read_only"
    ] is True

    assert len(
        result[
            "positions"
        ]
    ) == 1

    assert result[
        "positions"
    ][0][
        "symbol"
    ] == "TD.TO"


@pytest.mark.asyncio
async def test_readonly_positions_does_not_use_legacy_file_facade(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    principal = SimpleNamespace(
        subject="owner-456",
    )


    def forbidden_legacy_facade(
        *_args,
        **_kwargs,
    ):

        raise AssertionError(
            "legacy normalized-file portfolio facade was invoked"
        )


    async def fake_positions_service(
        supplied_principal,
    ):

        assert (
            supplied_principal
            is principal
        )

        return {
            "positions": [],
        }


    monkeypatch.setattr(
        main,
        "_owned_portfolio_facade_for_principal",
        forbidden_legacy_facade,
    )

    monkeypatch.setattr(
        main,
        "get_portfolio_positions_for_api",
        fake_positions_service,
    )


    result = await (
        main.authenticated_owned_portfolio_positions(
            principal=principal,
        )
    )


    assert result == {
        "status":
            "ok",

        "read_only":
            True,

        "positions":
            [],
    }
