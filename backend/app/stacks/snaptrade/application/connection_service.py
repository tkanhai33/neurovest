from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.stacks.snaptrade.adapters.sdk_client_factory import (
    build_snaptrade_sdk_client,
)
from backend.app.stacks.snaptrade.persistence.credential_repository import (
    SnapTradeCredentialRepository,
    serialize_snaptrade_credential_state,
)


class SnapTradeConnectionRejectedError(
    RuntimeError
):
    pass


class SnapTradeProviderUnavailableError(
    RuntimeError
):
    pass


def utc_now() -> datetime:
    return datetime.now(UTC)


def _extract_value(
    value: Any,
    *names: str,
) -> Any:
    """
    Extract a field from SDK response wrappers, mappings, generated
    response models, or parsed response objects.
    """

    if value is None:
        return None

    if isinstance(
        value,
        dict,
    ):
        for name in names:
            if name in value:
                return value[name]

    for container_name in (
        "parsed",
        "body",
        "data",
        "additional_properties",
    ):
        nested = getattr(
            value,
            container_name,
            None,
        )

        if nested is not None and nested is not value:
            extracted = _extract_value(
                nested,
                *names,
            )

            if extracted is not None:
                return extracted

    for name in names:
        if hasattr(
            value,
            name,
        ):
            return getattr(
                value,
                name,
            )

    return None


def _response_items(
    response: Any,
) -> list[Any]:
    candidate = response

    for container_name in (
        "parsed",
        "body",
        "data",
    ):
        nested = getattr(
            candidate,
            container_name,
            None,
        )

        if nested is not None:
            candidate = nested
            break

    if candidate is None:
        return []

    if isinstance(
        candidate,
        list,
    ):
        return candidate

    if isinstance(
        candidate,
        tuple,
    ):
        return list(candidate)

    if isinstance(
        candidate,
        dict,
    ):
        for key in (
            "accounts",
            "authorizations",
            "connections",
            "data",
            "results",
        ):
            nested = candidate.get(
                key
            )

            if isinstance(
                nested,
                list,
            ):
                return nested

        return [
            candidate
        ]

    try:
        if not isinstance(
            candidate,
            (
                str,
                bytes,
            ),
        ):
            return list(candidate)
    except TypeError:
        pass

    return [
        candidate
    ]


def _provider_sync_status(
    accounts: list[Any],
    authorizations: list[Any],
) -> str:
    statuses: list[str] = []

    for item in [
        *accounts,
        *authorizations,
    ]:
        status = _extract_value(
            item,
            "sync_status",
            "syncStatus",
            "status",
        )

        if status is None:
            continue

        rendered = str(
            status
        ).strip()

        if rendered:
            statuses.append(
                rendered
            )

    if not accounts and not authorizations:
        return "not_connected"

    if not statuses:
        return "available"

    lowered = {
        status.lower()
        for status in statuses
    }

    if any(
        token in status
        for status in lowered
        for token in (
            "error",
            "failed",
            "disabled",
        )
    ):
        return "provider_error"

    if any(
        token in status
        for status in lowered
        for token in (
            "sync",
            "refresh",
            "pending",
        )
    ):
        return "synchronizing"

    return "connected"


class SnapTradeConnectionService:
    """
    Owner-scoped SnapTrade onboarding and synchronization service.

    This service exposes registration, read-only connection portal
    generation, and read-only connection/account status only.

    It does not expose orders, trading, cancellation, replacement,
    or transaction execution.
    """

    def __init__(
        self,
        session: AsyncSession,
        *,
        client_factory: Callable[
            [],
            Any,
        ] = build_snaptrade_sdk_client,
    ) -> None:
        self._session = session
        self._client_factory = (
            client_factory
        )

        self._credentials = (
            SnapTradeCredentialRepository(
                session
            )
        )

    def _raw_client(
        self,
    ) -> Any:
        try:
            wrapper = (
                self._client_factory()
            )
        except Exception as exc:
            raise SnapTradeProviderUnavailableError(
                "SnapTrade client could not be constructed"
            ) from exc

        raw_client = getattr(
            wrapper,
            "_client",
            wrapper,
        )

        required_namespaces = (
            "authentication",
            "connections",
            "account_information",
        )

        missing = [
            name
            for name in required_namespaces
            if getattr(
                raw_client,
                name,
                None,
            )
            is None
        ]

        if missing:
            raise SnapTradeProviderUnavailableError(
                "SnapTrade client is missing required "
                "read-only namespaces"
            )

        return raw_client

    async def register_owner(
        self,
        *,
        neurovest_user_id: str,
    ) -> dict[str, object]:
        owner = str(
            neurovest_user_id
        ).strip()

        if not owner:
            raise SnapTradeConnectionRejectedError(
                "Authenticated owner is required"
            )

        existing = (
            await self._credentials
            .get_for_owner(
                owner
            )
        )

        if existing is not None:
            return (
                serialize_snaptrade_credential_state(
                    existing
                )
            )

        raw_client = self._raw_client()

        try:
            response = await asyncio.to_thread(
                raw_client.authentication
                .register_snap_trade_user,
                user_id=owner,
            )
        except Exception as exc:
            raise SnapTradeProviderUnavailableError(
                "SnapTrade registration failed"
            ) from exc

        snaptrade_user_id = _extract_value(
            response,
            "userId",
            "user_id",
        )

        user_secret = _extract_value(
            response,
            "userSecret",
            "user_secret",
        )

        if (
            not isinstance(
                snaptrade_user_id,
                str,
            )
            or not snaptrade_user_id.strip()
            or not isinstance(
                user_secret,
                str,
            )
            or not user_secret.strip()
        ):
            raise SnapTradeProviderUnavailableError(
                "SnapTrade registration returned an invalid identity"
            )

        record = (
            await self._credentials
            .store_registered_credential(
                neurovest_user_id=owner,
                snaptrade_user_id=(
                    snaptrade_user_id
                ),
                user_secret=user_secret,
            )
        )

        await self._session.commit()
        await self._session.refresh(
            record
        )

        return (
            serialize_snaptrade_credential_state(
                record
            )
        )

    async def create_readonly_portal(
        self,
        *,
        neurovest_user_id: str,
        custom_redirect: str | None = None,
        dark_mode: bool = True,
    ) -> dict[str, object]:
        owner = str(
            neurovest_user_id
        ).strip()

        if not owner:
            raise SnapTradeConnectionRejectedError(
                "Authenticated owner is required"
            )

        try:
            (
                snaptrade_user_id,
                user_secret,
            ) = (
                await self._credentials
                .load_provider_identity(
                    neurovest_user_id=owner
                )
            )
        except LookupError as exc:
            raise SnapTradeConnectionRejectedError(
                "SnapTrade registration is required"
            ) from exc

        raw_client = self._raw_client()

        request_kwargs: dict[
            str,
            object,
        ] = {
            "user_id": (
                snaptrade_user_id
            ),
            "user_secret": (
                user_secret
            ),
            "connection_type": "read",
            "immediate_redirect": False,
            "show_close_button": True,
            "dark_mode": bool(
                dark_mode
            ),
            "connection_portal_version": (
                "v4"
            ),
        }

        normalized_redirect = (
            str(
                custom_redirect
            ).strip()
            if custom_redirect
            else ""
        )

        if normalized_redirect:
            request_kwargs[
                "custom_redirect"
            ] = normalized_redirect

        try:
            response = await asyncio.to_thread(
                raw_client.authentication
                .login_snap_trade_user,
                **request_kwargs,
            )
        except Exception as exc:
            raise SnapTradeProviderUnavailableError(
                "SnapTrade connection portal could not be generated"
            ) from exc

        redirect_uri = _extract_value(
            response,
            "redirectURI",
            "redirectUri",
            "redirect_uri",
        )

        session_id = _extract_value(
            response,
            "sessionId",
            "session_id",
        )

        if (
            not isinstance(
                redirect_uri,
                str,
            )
            or not redirect_uri.strip()
        ):
            raise SnapTradeProviderUnavailableError(
                "SnapTrade did not return a connection portal"
            )

        return {
            "status": "available",
            "connection_type": "read",
            "trading_enabled": False,
            "redirect_uri": (
                redirect_uri
            ),
            "session_id": (
                str(session_id)
                if session_id is not None
                else None
            ),
        }

    async def synchronize_status(
        self,
        *,
        neurovest_user_id: str,
    ) -> dict[str, object]:
        owner = str(
            neurovest_user_id
        ).strip()

        if not owner:
            raise SnapTradeConnectionRejectedError(
                "Authenticated owner is required"
            )

        try:
            (
                snaptrade_user_id,
                user_secret,
            ) = (
                await self._credentials
                .load_provider_identity(
                    neurovest_user_id=owner
                )
            )
        except LookupError:
            return {
                "registered": False,
                "connection_status": (
                    "not_registered"
                ),
                "last_sync_status": None,
                "last_synced_at": None,
                "account_count": 0,
                "authorization_count": 0,
                "trading_enabled": False,
            }

        raw_client = self._raw_client()

        try:
            account_response = (
                await asyncio.to_thread(
                    raw_client
                    .account_information
                    .list_user_accounts,
                    user_id=(
                        snaptrade_user_id
                    ),
                    user_secret=(
                        user_secret
                    ),
                )
            )

            authorization_response = (
                await asyncio.to_thread(
                    raw_client.connections
                    .list_brokerage_authorizations,
                    user_id=(
                        snaptrade_user_id
                    ),
                    user_secret=(
                        user_secret
                    ),
                )
            )
        except Exception as exc:
            raise SnapTradeProviderUnavailableError(
                "SnapTrade synchronization status could not be retrieved"
            ) from exc

        accounts = _response_items(
            account_response
        )

        authorizations = _response_items(
            authorization_response
        )

        sync_status = (
            _provider_sync_status(
                accounts,
                authorizations,
            )
        )

        synchronized_at = utc_now()

        record = (
            await self._credentials
            .update_sync_state(
                neurovest_user_id=owner,
                sync_status=sync_status,
                synced_at=(
                    synchronized_at
                ),
            )
        )

        if sync_status == "not_connected":
            record.connection_status = (
                "registered"
            )

        elif sync_status == "provider_error":
            record.connection_status = (
                "error"
            )

        elif sync_status == "synchronizing":
            record.connection_status = (
                "synchronizing"
            )

        else:
            record.connection_status = (
                "connected"
            )

        await self._session.commit()
        await self._session.refresh(
            record
        )

        state = (
            serialize_snaptrade_credential_state(
                record
            )
        )

        state.update(
            {
                "account_count": len(
                    accounts
                ),
                "authorization_count": (
                    len(
                        authorizations
                    )
                ),
                "trading_enabled": False,
            }
        )

        return state

    async def get_local_status(
        self,
        *,
        neurovest_user_id: str,
    ) -> dict[str, object]:
        owner = str(
            neurovest_user_id
        ).strip()

        if not owner:
            raise SnapTradeConnectionRejectedError(
                "Authenticated owner is required"
            )

        record = (
            await self._credentials
            .get_for_owner(
                owner
            )
        )

        if record is None:
            return {
                "registered": False,
                "connection_status": (
                    "not_registered"
                ),
                "last_sync_status": None,
                "last_synced_at": None,
                "trading_enabled": False,
            }

        state = (
            serialize_snaptrade_credential_state(
                record
            )
        )

        state[
            "trading_enabled"
        ] = False

        return state
