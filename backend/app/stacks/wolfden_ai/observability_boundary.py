"""
Wolfden-owned non-persistent observability boundary.

This boundary deliberately owns no database session, repository,
journal-ledger persistence, portfolio mutation, execution, broker,
SnapTrade, file-writing, or network capability.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any


_LOGGER = logging.getLogger(
    "neurovest.wolfden_ai"
)


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

    if isinstance(value, bytes):
        return value.hex()

    if isinstance(value, Mapping):
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
class WolfdenObservation(
    Mapping[str, Any],
):
    """
    Immutable, non-persistent Wolfden observability event.
    """

    event_name: str
    source: str
    persistent: bool
    mutation_requested: bool
    payload: tuple[
        tuple[str, Any],
        ...,
    ]

    def __post_init__(
        self,
    ) -> None:
        if not self.event_name.strip():
            raise ValueError(
                "event_name cannot be empty"
            )

        if self.source != "wolfden_ai":
            raise ValueError(
                "source must be wolfden_ai"
            )

        if self.persistent:
            raise ValueError(
                "Wolfden observations cannot be persistent"
            )

        if self.mutation_requested:
            raise ValueError(
                "Wolfden observations cannot request mutation"
            )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "event_name": self.event_name,
            "source": self.source,
            "persistent": self.persistent,
            "mutation_requested": (
                self.mutation_requested
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
                "event_name",
                "source",
                "persistent",
                "mutation_requested",
                "payload",
            )
        )

    def __len__(
        self,
    ) -> int:
        return 5


async def record_wolfden_observation(
    *args: Any,
    **kwargs: Any,
) -> WolfdenObservation:
    """
    Record an in-process Wolfden observation through standard logging.

    This function performs no database, ledger, file, network,
    portfolio, execution, broker, or live-trading operation.
    """

    event_name_value = kwargs.pop(
        "event_name",
        "wolfden_signal_observed",
    )

    event_name = (
        str(event_name_value).strip()
        or "wolfden_signal_observed"
    )

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

    observation = WolfdenObservation(
        event_name=event_name,
        source="wolfden_ai",
        persistent=False,
        mutation_requested=False,
        payload=tuple(
            payload_items
        ),
    )

    _LOGGER.info(
        "wolfden_observation",
        extra={
            "wolfden_observation": (
                observation.to_dict()
            ),
        },
    )

    return observation


__all__ = [
    "WolfdenObservation",
    "record_wolfden_observation",
]
