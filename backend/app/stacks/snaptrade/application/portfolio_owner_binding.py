from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Mapping, Sequence


OWNER_BINDING_SCHEMA = (
    "neurovest.snaptrade_portfolio_owner_bindings"
)

OWNER_BINDING_SCHEMA_VERSION = 1

DEFAULT_OWNER_BINDING_REGISTRY = Path(
    "runtime/dev_auth/"
    "snaptrade_portfolio_owner_bindings.json"
)


class PortfolioOwnerBindingError(
    ValueError
):
    pass


class PortfolioOwnerBindingNotFound(
    LookupError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class PortfolioOwnerBinding:
    neurovest_user_id: str
    account_id_hashes: tuple[str, ...]


@dataclass(
    frozen=True,
    slots=True,
)
class PortfolioOwnerBindingRegistry:
    schema: str
    schema_version: int
    bindings: Mapping[
        str,
        PortfolioOwnerBinding,
    ]

    def resolve(
        self,
        neurovest_user_id: str,
    ) -> PortfolioOwnerBinding:
        normalized_user_id = _normalize_user_id(
            neurovest_user_id
        )

        binding = self.bindings.get(
            normalized_user_id
        )

        if binding is None:
            raise PortfolioOwnerBindingNotFound(
                "No SnapTrade portfolio binding exists "
                "for the authenticated NeuroVest user."
            )

        return binding


def _normalize_user_id(
    value: object,
) -> str:
    normalized = str(
        value
    ).strip()

    if not normalized:
        raise PortfolioOwnerBindingError(
            "Authenticated NeuroVest user ID cannot be empty."
        )

    return normalized


def _require_sha256(
    value: object,
) -> str:
    if not isinstance(
        value,
        str,
    ):
        raise PortfolioOwnerBindingError(
            "Account binding must contain SHA-256 hashes."
        )

    normalized = value.strip().lower()

    if len(normalized) != 64:
        raise PortfolioOwnerBindingError(
            "Account binding hash must contain 64 characters."
        )

    try:
        int(
            normalized,
            16,
        )
    except ValueError as error:
        raise PortfolioOwnerBindingError(
            "Account binding hash must be hexadecimal."
        ) from error

    return normalized


def hash_account_identifier(
    account_identifier: str,
) -> str:
    normalized = account_identifier.strip()

    if not normalized:
        raise PortfolioOwnerBindingError(
            "Account identifier cannot be empty."
        )

    return hashlib.sha256(
        normalized.encode(
            "utf-8"
        )
    ).hexdigest()


def load_portfolio_owner_binding_registry(
    path: Path | str = DEFAULT_OWNER_BINDING_REGISTRY,
) -> PortfolioOwnerBindingRegistry:
    registry_path = Path(
        path
    )

    if not registry_path.is_file():
        raise PortfolioOwnerBindingError(
            "SnapTrade portfolio owner-binding registry is missing."
        )

    document = json.loads(
        registry_path.read_text(
            encoding="utf-8",
        )
    )

    if not isinstance(
        document,
        dict,
    ):
        raise PortfolioOwnerBindingError(
            "Owner-binding registry must be a JSON object."
        )

    if document.get(
        "schema"
    ) != OWNER_BINDING_SCHEMA:
        raise PortfolioOwnerBindingError(
            "Unsupported owner-binding schema."
        )

    if document.get(
        "schema_version"
    ) != OWNER_BINDING_SCHEMA_VERSION:
        raise PortfolioOwnerBindingError(
            "Unsupported owner-binding schema version."
        )

    raw_bindings = document.get(
        "bindings"
    )

    if not isinstance(
        raw_bindings,
        dict,
    ):
        raise PortfolioOwnerBindingError(
            "Owner-binding registry bindings must be an object."
        )

    bindings: dict[
        str,
        PortfolioOwnerBinding,
    ] = {}

    claimed_account_hashes: dict[
        str,
        str,
    ] = {}

    for raw_user_id, raw_account_hashes in raw_bindings.items():
        user_id = _normalize_user_id(
            raw_user_id
        )

        if not isinstance(
            raw_account_hashes,
            list,
        ):
            raise PortfolioOwnerBindingError(
                "Each owner binding must contain an array "
                "of account hashes."
            )

        account_hashes = tuple(
            _require_sha256(
                value
            )
            for value in raw_account_hashes
        )

        if not account_hashes:
            raise PortfolioOwnerBindingError(
                "An owner binding must contain at least one account."
            )

        if len(
            set(
                account_hashes
            )
        ) != len(
            account_hashes
        ):
            raise PortfolioOwnerBindingError(
                "Duplicate account hash found in one owner binding."
            )

        for account_hash in account_hashes:
            existing_owner = claimed_account_hashes.get(
                account_hash
            )

            if (
                existing_owner is not None
                and existing_owner != user_id
            ):
                raise PortfolioOwnerBindingError(
                    "A SnapTrade account hash cannot be assigned "
                    "to multiple NeuroVest users."
                )

            claimed_account_hashes[
                account_hash
            ] = user_id

        bindings[
            user_id
        ] = PortfolioOwnerBinding(
            neurovest_user_id=user_id,
            account_id_hashes=tuple(
                sorted(
                    account_hashes
                )
            ),
        )

    return PortfolioOwnerBindingRegistry(
        schema=OWNER_BINDING_SCHEMA,
        schema_version=OWNER_BINDING_SCHEMA_VERSION,
        bindings=MappingProxyType(
            bindings
        ),
    )


def resolve_owned_account_hashes(
    *,
    neurovest_user_id: str,
    registry_path: Path | str = (
        DEFAULT_OWNER_BINDING_REGISTRY
    ),
) -> tuple[str, ...]:
    registry = load_portfolio_owner_binding_registry(
        registry_path
    )

    return registry.resolve(
        neurovest_user_id
    ).account_id_hashes


def filter_owned_accounts(
    *,
    neurovest_user_id: str,
    available_account_hashes: Sequence[str],
    registry_path: Path | str = (
        DEFAULT_OWNER_BINDING_REGISTRY
    ),
) -> tuple[str, ...]:
    owned_hashes = set(
        resolve_owned_account_hashes(
            neurovest_user_id=neurovest_user_id,
            registry_path=registry_path,
        )
    )

    available = {
        _require_sha256(
            value
        )
        for value in available_account_hashes
    }

    missing = owned_hashes - available

    if missing:
        raise PortfolioOwnerBindingError(
            "The owner binding references an account that "
            "is absent from the qualified portfolio snapshot."
        )

    return tuple(
        sorted(
            owned_hashes
            & available
        )
    )
