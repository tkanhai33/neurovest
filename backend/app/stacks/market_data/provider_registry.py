"""
Canonical in-memory market-data provider registry.

The registry owns provider registration, capability indexing, priority,
and deterministic provider selection.

It performs no network calls and does not modify application runtime
composition.
"""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock

from backend.app.stacks.market_data.dto import (
    MarketDataCapability,
)
from backend.app.stacks.market_data.provider_contract import (
    MarketDataProvider,
    verify_provider_shape,
)


class ProviderRegistryError(RuntimeError):
    """Base error for provider-registry failures."""


class ProviderAlreadyRegisteredError(
    ProviderRegistryError
):
    """Raised when a provider name is registered twice."""


class ProviderNotRegisteredError(
    ProviderRegistryError
):
    """Raised when a requested provider is absent."""


class ProviderCapabilityUnavailableError(
    ProviderRegistryError
):
    """Raised when no provider supports a capability."""


@dataclass(
    frozen=True,
    slots=True,
)
class RegisteredProvider:
    name: str
    provider: MarketDataProvider
    priority: int
    enabled: bool

    def supports(
        self,
        capability: MarketDataCapability,
    ) -> bool:
        return (
            self.enabled
            and self.provider.supports(
                capability
            )
        )


class ProviderRegistry:
    """
    Thread-safe provider ownership registry.

    Lower integer priority values are selected first.
    """

    def __init__(self) -> None:
        self._providers: dict[
            str,
            RegisteredProvider,
        ] = {}

        self._lock = RLock()

    @staticmethod
    def _normalize_name(
        value: str,
    ) -> str:
        name = value.strip().lower()

        if not name:
            raise ValueError(
                "provider name must not be empty"
            )

        return name

    def register(
        self,
        provider: MarketDataProvider,
        *,
        priority: int = 100,
        enabled: bool = True,
        replace: bool = False,
    ) -> RegisteredProvider:
        valid, missing = verify_provider_shape(
            provider
        )

        if not valid:
            raise TypeError(
                "provider does not satisfy the "
                "required runtime shape; missing: "
                + ", ".join(missing)
            )

        name = self._normalize_name(
            provider.provider_name
        )

        if priority < 0:
            raise ValueError(
                "priority must not be negative"
            )

        record = RegisteredProvider(
            name=name,
            provider=provider,
            priority=priority,
            enabled=enabled,
        )

        with self._lock:
            if (
                name in self._providers
                and not replace
            ):
                raise ProviderAlreadyRegisteredError(
                    f"provider already registered: {name}"
                )

            self._providers[name] = record

        return record

    def unregister(
        self,
        name: str,
    ) -> RegisteredProvider:
        normalized = self._normalize_name(
            name
        )

        with self._lock:
            try:
                return self._providers.pop(
                    normalized
                )

            except KeyError as exc:
                raise ProviderNotRegisteredError(
                    f"provider not registered: {normalized}"
                ) from exc

    def get(
        self,
        name: str,
        *,
        require_enabled: bool = True,
    ) -> MarketDataProvider:
        normalized = self._normalize_name(
            name
        )

        with self._lock:
            record = self._providers.get(
                normalized
            )

        if record is None:
            raise ProviderNotRegisteredError(
                f"provider not registered: {normalized}"
            )

        if (
            require_enabled
            and not record.enabled
        ):
            raise ProviderNotRegisteredError(
                f"provider is disabled: {normalized}"
            )

        return record.provider

    def set_enabled(
        self,
        name: str,
        enabled: bool,
    ) -> RegisteredProvider:
        normalized = self._normalize_name(
            name
        )

        with self._lock:
            existing = self._providers.get(
                normalized
            )

            if existing is None:
                raise ProviderNotRegisteredError(
                    f"provider not registered: {normalized}"
                )

            updated = RegisteredProvider(
                name=existing.name,
                provider=existing.provider,
                priority=existing.priority,
                enabled=enabled,
            )

            self._providers[
                normalized
            ] = updated

        return updated

    def records(
        self,
        *,
        include_disabled: bool = False,
    ) -> tuple[RegisteredProvider, ...]:
        with self._lock:
            records = tuple(
                self._providers.values()
            )

        filtered = (
            records
            if include_disabled
            else tuple(
                record
                for record in records
                if record.enabled
            )
        )

        return tuple(
            sorted(
                filtered,
                key=lambda record: (
                    record.priority,
                    record.name,
                ),
            )
        )

    def providers_for(
        self,
        capability: MarketDataCapability,
    ) -> tuple[MarketDataProvider, ...]:
        providers = tuple(
            record.provider
            for record in self.records()
            if record.supports(
                capability
            )
        )

        return providers

    def select(
        self,
        capability: MarketDataCapability,
    ) -> MarketDataProvider:
        providers = self.providers_for(
            capability
        )

        if not providers:
            raise ProviderCapabilityUnavailableError(
                "no enabled provider supports "
                f"{capability.value}"
            )

        return providers[0]

    def clear(self) -> None:
        with self._lock:
            self._providers.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(
                self._providers
            )


def healthcheck() -> dict[str, object]:
    """
    Compatibility health surface.

    This does not inspect external providers.
    """

    return {
        "component": "provider_registry",
        "healthy": True,
        "network_called": False,
    }
