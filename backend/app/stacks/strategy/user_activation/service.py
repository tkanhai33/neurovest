from __future__ import annotations

from typing import Any

from sqlalchemy import (
    delete,
    select,
)

from backend.app.stacks.db_runtime.database import async_session
from backend.app.stacks.strategy.reference_catalog.catalog import (
    get_reference_strategies,
    get_reference_strategy,
)

from .model import (
    UserStrategyActivation,
    UserStrategyUniverseMember,
)

from .applicability import (
    enrich_reference_strategy,
    strategy_matches_market_filter,
)


MAX_ENABLED_STRATEGIES = 361


def _clean_owner_subject(
    owner_subject: str,
) -> str:

    value = str(
        owner_subject
        or ""
    ).strip()

    if not value:
        raise ValueError(
            "owner_subject is required."
        )

    return value


def _clean_strategy_name(
    strategy_name: str,
) -> str:

    value = str(
        strategy_name
        or ""
    ).strip()

    if not value:
        raise ValueError(
            "strategy_name is required."
        )

    return value


def _catalog_names() -> set[str]:

    return {
        str(
            row.get(
                "strategy_name"
            )
            or ""
        ).strip()
        for row
        in get_reference_strategies()
        if str(
            row.get(
                "strategy_name"
            )
            or ""
        ).strip()
    }


def list_reference_library(
    *,
    market: str | None = None,
) -> list[dict[str, Any]]:

    rows = []

    for raw in get_reference_strategies():

        row = dict(
            raw
        )

        if not strategy_matches_market_filter(
            row,
            market,
        ):
            continue

        rows.append(
            enrich_reference_strategy(
                row
            )
        )

    return rows


async def list_enabled_strategy_names(
    *,
    owner_subject: str,
) -> list[str]:

    owner = _clean_owner_subject(
        owner_subject
    )

    async with async_session() as session:

        result = await session.execute(
            select(
                UserStrategyActivation.strategy_name
            )
            .where(
                UserStrategyActivation.owner_subject
                == owner
            )
            .where(
                UserStrategyActivation.enabled
                .is_(True)
            )
            .order_by(
                UserStrategyActivation.strategy_name.asc()
            )
        )

        return [
            str(value)
            for value
            in result.scalars().all()
        ]


async def list_enabled_reference_strategies(
    *,
    owner_subject: str,
) -> list[dict[str, Any]]:

    names = await list_enabled_strategy_names(
        owner_subject=owner_subject,
    )

    enabled = []

    for name in names:

        row = get_reference_strategy(
            name
        )

        if row is not None:
            enabled.append(
                dict(row)
            )

    return enabled


async def replace_enabled_strategies(
    *,
    owner_subject: str,
    strategy_names: list[str],
) -> list[str]:

    owner = _clean_owner_subject(
        owner_subject
    )

    cleaned = []

    seen = set()

    for raw in strategy_names:

        name = _clean_strategy_name(
            raw
        )

        if name in seen:
            continue

        seen.add(name)
        cleaned.append(name)


    if len(cleaned) > MAX_ENABLED_STRATEGIES:

        raise ValueError(
            "Too many enabled strategies."
        )


    valid_names = _catalog_names()

    unknown = sorted(
        set(cleaned)
        - valid_names
    )

    if unknown:

        raise ValueError(
            "Unknown reference strategies: "
            + ", ".join(
                unknown[:10]
            )
        )


    async with async_session() as session:

        async with session.begin():

            await session.execute(
                delete(
                    UserStrategyActivation
                ).where(
                    UserStrategyActivation.owner_subject
                    == owner
                )
            )


            for name in cleaned:

                session.add(
                    UserStrategyActivation(
                        owner_subject=owner,
                        strategy_name=name,
                        enabled=True,
                    )
                )


    return sorted(
        cleaned
    )


async def clear_enabled_strategies(
    *,
    owner_subject: str,
) -> None:

    owner = _clean_owner_subject(
        owner_subject
    )

    async with async_session() as session:

        async with session.begin():

            await session.execute(
                delete(
                    UserStrategyActivation
                ).where(
                    UserStrategyActivation.owner_subject
                    == owner
                )
            )


DEFAULT_OWNER_UNIVERSE_NAME = "default"
MAX_OWNER_UNIVERSE_SYMBOLS = 32


def _clean_universe_name(
    universe_name: object,
) -> str:
    name = str(universe_name).strip().lower()

    if not name:
        raise ValueError("universe_name must not be empty")

    if len(name) > 64:
        raise ValueError("universe_name must be at most 64 characters")

    return name


def _clean_owner_universe_symbols(
    symbols: object,
) -> list[str]:
    if isinstance(symbols, (str, bytes)):
        raise ValueError(
            "universe symbols must be a list of individual symbols"
        )

    try:
        values = iter(symbols)
    except TypeError as exc:
        raise ValueError(
            "universe symbols must be iterable"
        ) from exc

    cleaned: list[str] = []
    seen: set[str] = set()

    for raw_symbol in values:
        symbol = str(raw_symbol).strip().upper()

        if not symbol:
            raise ValueError(
                "universe symbols must not contain an empty value"
            )

        if len(symbol) > 32:
            raise ValueError(
                "universe symbols must be at most 32 characters"
            )

        if symbol in seen:
            continue

        seen.add(symbol)
        cleaned.append(symbol)

    if len(cleaned) < 2:
        raise ValueError(
            "an owner universe requires at least two distinct symbols"
        )

    if len(cleaned) > MAX_OWNER_UNIVERSE_SYMBOLS:
        raise ValueError(
            "an owner universe supports at most "
            f"{MAX_OWNER_UNIVERSE_SYMBOLS} symbols"
        )

    return cleaned


async def list_owner_universe_symbols(
    *,
    owner_subject: str,
    universe_name: str = DEFAULT_OWNER_UNIVERSE_NAME,
) -> list[str]:
    owner = _clean_owner_subject(owner_subject)
    universe = _clean_universe_name(universe_name)

    async with async_session() as session:
        result = await session.execute(
            select(UserStrategyUniverseMember.symbol)
            .where(
                UserStrategyUniverseMember.owner_subject
                == owner
            )
            .where(
                UserStrategyUniverseMember.universe_name
                == universe
            )
            .order_by(
                UserStrategyUniverseMember.symbol.asc()
            )
        )

        return [
            str(value)
            for value in result.scalars().all()
        ]


async def replace_owner_universe_symbols(
    *,
    owner_subject: str,
    symbols: object,
    universe_name: str = DEFAULT_OWNER_UNIVERSE_NAME,
) -> list[str]:
    owner = _clean_owner_subject(owner_subject)
    universe = _clean_universe_name(universe_name)
    cleaned_symbols = _clean_owner_universe_symbols(symbols)

    async with async_session() as session:
        existing_result = await session.execute(
            select(UserStrategyUniverseMember)
            .where(
                UserStrategyUniverseMember.owner_subject
                == owner
            )
            .where(
                UserStrategyUniverseMember.universe_name
                == universe
            )
        )

        for row in existing_result.scalars().all():
            await session.delete(row)

        session.add_all(
            [
                UserStrategyUniverseMember(
                    owner_subject=owner,
                    universe_name=universe,
                    symbol=symbol,
                )
                for symbol in cleaned_symbols
            ]
        )

        await session.commit()

    return sorted(cleaned_symbols)
