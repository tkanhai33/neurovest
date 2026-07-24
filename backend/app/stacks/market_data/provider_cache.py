"""
Bounded thread-safe TTL cache for canonical market-data results.

The cache is in-memory, process-local, deterministic, and performs no
network activity.
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from threading import RLock
from time import monotonic
from typing import Callable, Generic, Hashable, TypeVar


KeyT = TypeVar(
    "KeyT",
    bound=Hashable,
)

ValueT = TypeVar(
    "ValueT",
)


@dataclass(
    frozen=True,
    slots=True,
)
class CacheStats:
    size: int
    maximum_size: int
    hits: int
    misses: int
    expirations: int
    evictions: int


@dataclass(
    slots=True,
)
class _CacheEntry:
    value: object
    expires_at: float


class MarketDataCache(
    Generic[
        KeyT,
        ValueT,
    ]
):
    """Bounded least-recently-used TTL cache."""

    def __init__(
        self,
        *,
        maximum_size: int = 1024,
        default_ttl_seconds: float = 30.0,
        clock: Callable[
            [],
            float,
        ] = monotonic,
    ) -> None:
        if maximum_size <= 0:
            raise ValueError(
                "maximum_size must be greater than zero"
            )

        if default_ttl_seconds <= 0:
            raise ValueError(
                "default_ttl_seconds must be greater than zero"
            )

        self._maximum_size = maximum_size
        self._default_ttl_seconds = (
            float(
                default_ttl_seconds
            )
        )
        self._clock = clock
        self._entries: OrderedDict[
            KeyT,
            _CacheEntry,
        ] = OrderedDict()
        self._lock = RLock()

        self._hits = 0
        self._misses = 0
        self._expirations = 0
        self._evictions = 0

    def set(
        self,
        key: KeyT,
        value: ValueT,
        *,
        ttl_seconds: float | None = None,
    ) -> None:
        ttl = (
            self._default_ttl_seconds
            if ttl_seconds is None
            else float(ttl_seconds)
        )

        if ttl <= 0:
            raise ValueError(
                "ttl_seconds must be greater than zero"
            )

        expires_at = (
            self._clock()
            + ttl
        )

        with self._lock:
            self._entries.pop(
                key,
                None,
            )

            self._entries[key] = (
                _CacheEntry(
                    value=value,
                    expires_at=expires_at,
                )
            )

            while (
                len(self._entries)
                > self._maximum_size
            ):
                self._entries.popitem(
                    last=False
                )
                self._evictions += 1

    def get(
        self,
        key: KeyT,
    ) -> ValueT | None:
        now = self._clock()

        with self._lock:
            entry = self._entries.get(
                key
            )

            if entry is None:
                self._misses += 1
                return None

            if entry.expires_at <= now:
                self._entries.pop(
                    key,
                    None,
                )
                self._misses += 1
                self._expirations += 1
                return None

            self._entries.move_to_end(
                key
            )
            self._hits += 1

            return entry.value  # type: ignore[return-value]

    def delete(
        self,
        key: KeyT,
    ) -> bool:
        with self._lock:
            return (
                self._entries.pop(
                    key,
                    None,
                )
                is not None
            )

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()

    def purge_expired(self) -> int:
        now = self._clock()
        removed = 0

        with self._lock:
            expired_keys = [
                key
                for key, entry
                in self._entries.items()
                if entry.expires_at
                <= now
            ]

            for key in expired_keys:
                self._entries.pop(
                    key,
                    None,
                )
                removed += 1

            self._expirations += removed

        return removed

    def stats(self) -> CacheStats:
        with self._lock:
            return CacheStats(
                size=len(
                    self._entries
                ),
                maximum_size=(
                    self._maximum_size
                ),
                hits=self._hits,
                misses=self._misses,
                expirations=(
                    self._expirations
                ),
                evictions=self._evictions,
            )

    def __len__(self) -> int:
        with self._lock:
            return len(
                self._entries
            )


def healthcheck() -> dict[str, object]:
    return {
        "component": "provider_cache",
        "healthy": True,
        "network_called": False,
    }
