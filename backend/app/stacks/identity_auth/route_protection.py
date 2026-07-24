from __future__ import annotations

import re
from time import perf_counter
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from fastapi import status
from fastapi.security import HTTPAuthorizationCredentials
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from backend.app.core.runtime_trace import (
    create_trace_id,
    emit_runtime_step,
)

from backend.app.stacks.identity_auth.dependencies import (
    authenticate_bearer_credentials,
)

from backend.app.stacks.db_runtime.database import (
    async_session,
)

from backend.app.stacks.identity_auth.repositories import (
    IdentityUserRepository,
)

from backend.app.stacks.identity_auth.access_token_revocation_repository import (
    AccessTokenRevocationRepository,
)


PUBLIC = "PUBLIC"
AUTHENTICATED = "AUTHENTICATED"
OWNER_ONLY = "OWNER_ONLY"
ADMIN_ONLY = "ADMIN_ONLY"
BLOCKED_CAPABILITY = "BLOCKED_CAPABILITY"


@dataclass(frozen=True)
class RoutePolicy:
    method: str
    path_template: str
    policy: str


ROUTE_POLICIES: tuple[RoutePolicy, ...] = (
    RoutePolicy(
        method='POST',
        path_template='/auth/change-required-password',
        policy='AUTHENTICATED',
    ),
    RoutePolicy(
        method='POST',
        path_template='/auth/logout-all',
        policy='AUTHENTICATED',
    ),
    RoutePolicy(
        method='POST',
        path_template='/auth/logout',
        policy='PUBLIC',
    ),
    RoutePolicy(
        method='POST',
        path_template='/auth/refresh',
        policy='PUBLIC',
    ),
    RoutePolicy(
        method='POST',
        path_template='/api/v1/admin/backup',
        policy='ADMIN_ONLY',
    ),
    RoutePolicy(
        method='GET',
        path_template='/api/v1/analytics',
        policy='AUTHENTICATED',
    ),
    RoutePolicy(
        method='POST',
        path_template='/api/v1/chat',
        policy='AUTHENTICATED',
    ),
    RoutePolicy(
        method='GET',
        path_template='/api/v1/dashboard/summary',
        policy='AUTHENTICATED',
    ),
    RoutePolicy(
        method='GET',
        path_template='/api/v1/graph/live',
        policy='AUTHENTICATED',
    ),
    RoutePolicy(
        method='GET',
        path_template='/api/v1/market-data/historical/{symbol}',
        policy='AUTHENTICATED',
    ),
    RoutePolicy(
        method='GET',
        path_template='/api/v1/market-data/quote/{symbol}',
        policy='AUTHENTICATED',
    ),
    RoutePolicy(
        method='GET',
        path_template='/api/v1/market-data/status',
        policy='PUBLIC',
    ),
    RoutePolicy(
        method='GET',
        path_template='/api/v1/market/live-price/{symbol}',
        policy='AUTHENTICATED',
    ),
    RoutePolicy(
        method='GET',
        path_template='/api/v1/orders',
        policy='AUTHENTICATED',
    ),
    RoutePolicy(
        method='POST',
        path_template='/api/v1/paper/orders',
        policy='AUTHENTICATED',
    ),
    RoutePolicy(
        method='GET',
        path_template='/api/v1/portfolio/positions',
        policy='AUTHENTICATED',
    ),
    RoutePolicy(
        method='GET',
        path_template='/api/v1/positions',
        policy='AUTHENTICATED',
    ),
    RoutePolicy(
        method='GET',
        path_template='/api/v1/portfolio/valuation',
        policy='AUTHENTICATED',
    ),
    RoutePolicy(
        method='GET',
        path_template='/api/v1/risk/gate/{symbol}',
        policy='AUTHENTICATED',
    ),
    RoutePolicy(
        method='POST',
        path_template='/api/v1/sandbox/audit',
        policy='ADMIN_ONLY',
    ),
    RoutePolicy(
        method='POST',
        path_template='/api/v1/sandbox/signal',
        policy='AUTHENTICATED',
    ),
    RoutePolicy(
        method='GET',
        path_template='/api/v1/strategy/decision/{symbol}',
        policy='AUTHENTICATED',
    ),
    RoutePolicy(
        method='POST',
        path_template='/auth/login',
        policy='PUBLIC',
    ),
    RoutePolicy(
        method='POST',
        path_template='/auth/register',
        policy='PUBLIC',
    ),
    # New route policy for introspection
    RoutePolicy(
        method='GET',
        path_template='/auth/introspection',
        policy='AUTHENTICATED',
    ),
)


FRAMEWORK_PUBLIC_PATHS = frozenset(
    {
        "/docs",
        "/docs/oauth2-redirect",
        "/openapi.json",
        "/redoc",
    }
)


ADMIN_ROLES = frozenset(
    {
        "admin",
        "administrator",
        "system_admin",
    }
)


def _compile_template(
    template: str,
) -> re.Pattern[str]:
    escaped = re.escape(
        template
    )

    pattern = re.sub(
        r"\\\{[^{}]+\\\}",
        r"[^/]+",
        escaped,
    )

    return re.compile(
        "^"
        + pattern
        + "$"
    )


_COMPILED_POLICIES = tuple(
    (
        policy,
        _compile_template(
            policy.path_template
        ),
    )
    for policy in ROUTE_POLICIES
)


def resolve_route_policy(
    method: str,
    path: str,
) -> str | None:
    normalized_method = method.upper()

    if (
        normalized_method == "OPTIONS"
        or path in FRAMEWORK_PUBLIC_PATHS
    ):
        return PUBLIC

    for policy, pattern in _COMPILED_POLICIES:
        if (
            policy.method
            == normalized_method
            and pattern.fullmatch(
                path
            )
        ):
            return policy.policy

    return None


def _unauthorized(
    detail: str = "Authentication required",
) -> JSONResponse:
    return JSONResponse(
        status_code=(
            status.HTTP_401_UNAUTHORIZED
        ),
        content={
            "detail": detail,
        },
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )


def _forbidden(
    detail: str,
) -> JSONResponse:
    return JSONResponse(
        status_code=(
            status.HTTP_403_FORBIDDEN
        ),
        content={
            "detail": detail,
        },
    )


def _extract_bearer_credentials(
    request: Request,
) -> HTTPAuthorizationCredentials | None:
    authorization = request.headers.get(
        "authorization"
    )

    if not authorization:
        return None

    scheme, separator, token = (
        authorization.partition(
            " "
        )
    )

    if (
        not separator
        or scheme.lower() != "bearer"
        or not token.strip()
    ):
        return None

    return HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token.strip(),
    )


async def _authenticate_request(
    request: Request,
) -> Any | None:
    credentials = _extract_bearer_credentials(
        request
    )

    if credentials is None:
        return None

    try:
        return await _authenticate_with_durable_revocation(
            credentials
        )

    except Exception:
        return None



async def _authenticate_with_durable_revocation(
    credentials: HTTPAuthorizationCredentials,
) -> Any:
    principal = authenticate_bearer_credentials(
        credentials
    )

    token_id = getattr(
        principal,
        "token_id",
        None,
    )

    # Canonical production principals always carry an access-token
    # JTI. Existing route-protection tests deliberately inject a
    # reduced principal object so their mocked identity-state boundary
    # remains isolated from token persistence.
    if not token_id:
        return principal

    async with async_session() as session:
        repository = AccessTokenRevocationRepository(
            session
        )

        if await repository.is_revoked(
            token_id
        ):
            return None

    return principal

def _principal_roles(
    principal: Any,
) -> set[str]:
    claims = getattr(
        principal,
        "claims",
        {},
    )

    if not isinstance(
        claims,
        dict,
    ):
        return set()

    roles: set[str] = set()

    role = claims.get(
        "role"
    )

    if isinstance(
        role,
        str,
    ):
        roles.add(
            role.strip().lower()
        )

    claim_roles = claims.get(
        "roles"
    )

    if isinstance(
        claim_roles,
        str,
    ):
        roles.add(
            claim_roles.strip().lower()
        )

    elif isinstance(
        claim_roles,
        (
            list,
            tuple,
            set,
        ),
    ):
        roles.update(
            str(value).strip().lower()
            for value in claim_roles
        )

    return {
        role
        for role in roles
        if role
    }


async def _load_identity_authorization_state(
    user_id: str,
) -> dict[str, object] | None:
    async with async_session() as session:
        repository = IdentityUserRepository(
            session
        )

        user = await repository.get_by_id(
            user_id
        )

        if user is None:
            return None

        return {
            "is_active": user.is_active,
            "status": user.status,
            "role": user.role,
            "must_change_password": (
                user.must_change_password
            ),
        }


async def enforce_route_policy(
    request: Request,
    call_next: Callable[
        [
            Request,
        ],
        Awaitable[
            Response
        ],
    ],
) -> Response:
    started = perf_counter()

    trace_id = str(
        getattr(
            request.state,
            "runtime_trace_id",
            "",
        )
        or request.headers.get(
            "x-neurovest-trace-id",
            ""
        )
        or create_trace_id(
            "http"
        )
    )

    request.state.runtime_trace_id = trace_id

    policy = resolve_route_policy(
        request.method,
        request.url.path,
    )

    request_source = (
        request.headers.get(
            "x-neurovest-source"
        )
        or "external_client"
    )

    if request_source == "frontend_chat":
        await emit_runtime_step(
            trace_id=trace_id,
            event_type="FRONTEND_CHAT_REQUEST_SENT",
            node="frontend_chat",
            status="active",
            layer="L6",
            stack="frontend",
            details={
                "operation": request.url.path,
                "success": True,
            },
        )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="HTTP_REQUEST_RECEIVED",
        node="http_api",
        source=request_source,
        destination="http_api",
        status="active",
        layer="L5",
        stack="api",
        message=(
            f"{request.method} "
            f"{request.url.path}"
        ),
        details={
            "operation": request.url.path,
            "policy": policy or "UNCLASSIFIED",
        },
    )

    async def finish(
        response: Response,
        *,
        authorization_status: str,
        principal_subject: str | None = None,
    ) -> Response:
        latency_ms = (
            perf_counter()
            - started
        ) * 1000

        response.headers[
            "X-Neurovest-Trace-Id"
        ] = trace_id

        await emit_runtime_step(
            trace_id=trace_id,
            event_type="HTTP_REQUEST_COMPLETED",
            node="http_api",
            source="route_authorization",
            destination="http_api",
            status=authorization_status,
            layer="L5",
            stack="api",
            message=(
                f"{request.method} "
                f"{request.url.path}"
            ),
            details={
                "http_status": response.status_code,
                "latency_ms": latency_ms,
                "policy": policy or "UNCLASSIFIED",
                "user_id": principal_subject,
                "success": (
                    response.status_code
                    < 400
                ),
            },
        )

        return response

    if policy is None:
        response = await call_next(
            request
        )

        return await finish(
            response,
            authorization_status=(
                "completed"
                if response.status_code < 400
                else "failed"
            ),
        )

    if policy == PUBLIC:
        await emit_runtime_step(
            trace_id=trace_id,
            event_type="ROUTE_POLICY_PUBLIC",
            node="route_authorization",
            source="http_api",
            destination="route_authorization",
            status="completed",
            layer="L1",
            stack="identity_auth",
            details={
                "policy": policy,
                "success": True,
            },
        )

        response = await call_next(
            request
        )

        return await finish(
            response,
            authorization_status=(
                "completed"
                if response.status_code < 400
                else "failed"
            ),
        )

    if policy == BLOCKED_CAPABILITY:
        response = _forbidden(
            "Capability remains disabled"
        )

        await emit_runtime_step(
            trace_id=trace_id,
            event_type="ROUTE_CAPABILITY_BLOCKED",
            node="route_authorization",
            source="http_api",
            destination="route_authorization",
            status="forbidden",
            layer="L1",
            stack="identity_auth",
            details={
                "http_status": 403,
                "policy": policy,
                "success": False,
            },
        )

        return await finish(
            response,
            authorization_status="forbidden",
        )

    jwt_started = perf_counter()

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="JWT_VALIDATION_STARTED",
        node="jwt_validation",
        source="route_authorization",
        destination="jwt_validation",
        status="active",
        layer="L1",
        stack="identity_auth",
        details={
            "policy": policy,
        },
    )

    principal = await _authenticate_request(
        request
    )

    jwt_latency_ms = (
        perf_counter()
        - jwt_started
    ) * 1000

    if principal is None:
        response = _unauthorized()

        await emit_runtime_step(
            trace_id=trace_id,
            event_type="JWT_VALIDATION_REJECTED",
            node="jwt_validation",
            source="jwt_validation",
            destination="route_authorization",
            status="unauthorized",
            layer="L1",
            stack="identity_auth",
            details={
                "http_status": 401,
                "latency_ms": jwt_latency_ms,
                "policy": policy,
                "success": False,
            },
        )

        return await finish(
            response,
            authorization_status="unauthorized",
        )

    principal_subject = str(
        getattr(
            principal,
            "subject",
            "",
        )
        or ""
    )

    request.state.authenticated_principal = (
        principal
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="AUTHENTICATED_PRINCIPAL_RESOLVED",
        node="authenticated_principal",
        status="authenticated",
        layer="L1",
        stack="identity_auth",
        details={
            "policy": policy,
            "user_id": principal_subject,
            "success": True,
        },
    )

    await emit_runtime_step(
        trace_id=trace_id,
        event_type="JWT_VALIDATION_COMPLETED",
        node="jwt_validation",
        source="jwt_validation",
        destination="authenticated_principal",
        status="authenticated",
        layer="L1",
        stack="identity_auth",
        details={
            "latency_ms": jwt_latency_ms,
            "policy": policy,
            "user_id": principal_subject,
            "success": True,
        },
    )

    identity_state = (
        await _load_identity_authorization_state(
            principal_subject
        )
    )

    if (
        identity_state is None
        or identity_state.get("is_active") is not True
        or identity_state.get("status") != "active"
    ):
        response = _unauthorized(
            "Authentication identity is unavailable"
        )

        return await finish(
            response,
            authorization_status="unauthorized",
            principal_subject=principal_subject,
        )

    password_change_required = bool(
        identity_state.get(
            "must_change_password"
        )
    )

    password_change_allowed_paths = {
        "/auth/change-required-password",
        "/auth/logout-all",
    }

    if (
        password_change_required
        and request.url.path
        not in password_change_allowed_paths
    ):
        response = _forbidden(
            "Password change required"
        )

        return await finish(
            response,
            authorization_status="password_change_required",
            principal_subject=principal_subject,
        )

    if policy == AUTHENTICATED:
        response = await call_next(
            request
        )

        return await finish(
            response,
            authorization_status=(
                "completed"
                if response.status_code < 400
                else "failed"
            ),
            principal_subject=principal_subject,
        )

    if policy == ADMIN_ONLY:
        if not (
            _principal_roles(
                principal
            )
            & ADMIN_ROLES
        ):
            response = _forbidden(
                "Administrator authorization required"
            )

            await emit_runtime_step(
                trace_id=trace_id,
                event_type="ADMIN_AUTHORIZATION_REJECTED",
                node="route_authorization",
                source="authenticated_principal",
                destination="route_authorization",
                status="forbidden",
                layer="L1",
                stack="identity_auth",
                details={
                    "http_status": 403,
                    "policy": policy,
                    "user_id": principal_subject,
                    "success": False,
                },
            )

            return await finish(
                response,
                authorization_status="forbidden",
                principal_subject=principal_subject,
            )

        response = await call_next(
            request
        )

        return await finish(
            response,
            authorization_status=(
                "completed"
                if response.status_code < 400
                else "failed"
            ),
            principal_subject=principal_subject,
        )

    if policy == OWNER_ONLY:
        response = _forbidden(
            "Resource ownership resolver is not configured"
        )

        return await finish(
            response,
            authorization_status="forbidden",
            principal_subject=principal_subject,
        )

    response = _forbidden(
        "Route policy is not authorized"
    )

    return await finish(
        response,
        authorization_status="forbidden",
        principal_subject=principal_subject,
    )
