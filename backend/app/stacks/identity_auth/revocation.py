from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock


@dataclass
class InMemoryTokenRevocationStore:
    """
    Process-local revocation boundary for qualification.

    This store deliberately performs no database writes.
    A durable owner may replace it only through a separately
    authorized persistence qualification.
    """

    _revoked: set[str] = field(
        default_factory=set,
        init=False,
        repr=False,
    )

    _lock: RLock = field(
        default_factory=RLock,
        init=False,
        repr=False,
    )

    def revoke(
        self,
        token_id: str,
    ) -> None:
        if not token_id:
            raise ValueError(
                "Token identifier cannot be empty"
            )

        with self._lock:
            self._revoked.add(
                token_id
            )

    def is_revoked(
        self,
        token_id: str,
    ) -> bool:
        with self._lock:
            return token_id in self._revoked
