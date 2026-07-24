"""
Immutable Wolfden-owned portfolio-output result boundary.

This module deliberately owns no execution, portfolio mutation,
database, ledger, broker, SnapTrade, session, or persistence capability.

Wolfden may describe an advisory result. It may not apply that result.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any


def _freeze_value(
    value: Any,
) -> Any:
    if value is None or isinstance(
        value,
        (
            bool,
            int,
            float,
            str,
        ),
    ):
        return value

    if isinstance(
        value,
        bytes,
    ):
        return value.hex()

    if isinstance(
        value,
        Mapping,
    ):
        return tuple(
            sorted(
                (
                    str(key),
                    _freeze_value(item),
                )
                for key, item
                in value.items()
            )
        )

    if isinstance(
        value,
        (
            list,
            tuple,
            set,
            frozenset,
        ),
    ):
        return tuple(
            _freeze_value(item)
            for item in value
        )

    model_dump = getattr(
        value,
        "model_dump",
        None,
    )

    if callable(model_dump):
        try:
            return _freeze_value(
                model_dump()
            )

        except Exception:
            return repr(value)

    return repr(value)


@dataclass(
    frozen=True,
    slots=True,
)
class WolfdenPortfolioOutputResult(
    Mapping[str, Any],
):
    """
    Non-executable result produced by wolfden_ai.

    This DTO cannot apply portfolio changes, write to a ledger,
    access a database session, place an order, or invoke a broker.
    """

    status: str
    source: str
    executable: bool
    mutation_applied: bool
    broker_requested: bool
    payload: tuple[
        tuple[str, Any],
        ...,
    ]

    def __post_init__(
        self,
    ) -> None:
        if self.executable:
            raise ValueError(
                "Wolfden portfolio output cannot be executable"
            )

        if self.mutation_applied:
            raise ValueError(
                "Wolfden portfolio output cannot apply mutations"
            )

        if self.broker_requested:
            raise ValueError(
                "Wolfden portfolio output cannot request a broker"
            )

        if not self.status.strip():
            raise ValueError(
                "status cannot be empty"
            )

        if self.source != "wolfden_ai":
            raise ValueError(
                "source must be wolfden_ai"
            )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "status": self.status,
            "source": self.source,
            "executable": self.executable,
            "mutation_applied": (
                self.mutation_applied
            ),
            "broker_requested": (
                self.broker_requested
            ),
            "payload": dict(
                self.payload
            ),
        }

    def as_read_only_mapping(
        self,
    ) -> Mapping[str, Any]:
        return MappingProxyType(
            self.to_dict()
        )

    def __getitem__(
        self,
        key: str,
    ) -> Any:
        return self.to_dict()[key]

    def __iter__(
        self,
    ) -> Iterator[str]:
        return iter(
            (
                "status",
                "source",
                "executable",
                "mutation_applied",
                "broker_requested",
                "payload",
            )
        )

    def __len__(
        self,
    ) -> int:
        return 6


def build_portfolio_output_result(
    *args: Any,
    **kwargs: Any,
) -> WolfdenPortfolioOutputResult:
    """
    Convert Wolfden advisory inputs into an immutable result.

    The function intentionally performs no execution, portfolio mutation,
    database operation, ledger write, network request, or broker action.
    """

    payload_items = [
        (
            f"arg_{index}",
            _freeze_value(value),
        )
        for index, value
        in enumerate(args)
    ]

    payload_items.extend(
        (
            str(key),
            _freeze_value(value),
        )
        for key, value
        in sorted(
            kwargs.items()
        )
    )

    return WolfdenPortfolioOutputResult(
        status="ADVISORY_ONLY",
        source="wolfden_ai",
        executable=False,
        mutation_applied=False,
        broker_requested=False,
        payload=tuple(
            payload_items
        ),
    )


__all__ = [
    "WolfdenPortfolioOutputResult",
    "build_portfolio_output_result",
]
