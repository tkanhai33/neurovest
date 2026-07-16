from __future__ import annotations

from datetime import UTC, datetime

from typing import Protocol

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from backend.app.stacks.identity_auth.api_dependencies import (
    get_login_api_service,
    get_registration_api_service,
    get_required_password_change_service,
    get_session_lifecycle_api_service,
    require_authenticated_principal,
    optional_logout_access_principal,
)

from backend.app.stacks.identity_auth.api_models import (
    ChangeRequiredPasswordApiRequest,
    ChangeRequiredPasswordApiResponse,
    LoginApiRequest,
    LoginTokenApiResponse,
    LogoutAllApiResponse,
    LogoutApiRequest,
    RefreshTokenApiRequest,
    RegistrationApiRequest,
    RegistrationApiResponse,
    SessionActionApiResponse,
    SessionTokenApiResponse,
)

from backend.app.stacks.identity_auth.service_contracts import (
    AuthenticationTokenPair,
    LoginCommand,
    RegisteredIdentity,
    RegistrationCommand,
)

from backend.app.stacks.identity_auth.session_lifecycle_service import (
    SessionLifecycleRejectedError,
    SessionLifecycleService,
)

from backend.app.stacks.identity_auth.password_change_service import (
    PasswordChangeRejectedError,
    RequiredPasswordChangeService,
)


class RegistrationApiService(
    Protocol
):
    async def register(
        self,
        command: RegistrationCommand,
    ) -> RegisteredIdentity:
        ...


class LoginApiService(
    Protocol
):
    async def login(
        self,
        command: LoginCommand,
    ) -> AuthenticationTokenPair:
        ...


class SessionLifecycleApiService(
    Protocol
):
    async def refresh(
        self,
        *,
        refresh_token: str,
    ) -> AuthenticationTokenPair:
        ...

    async def logout(
        self,
        *,
        refresh_token: str,
    ) -> None:
        ...

    async def logout_all(
        self,
        *,
        user_id: str,
    ) -> int:
        ...


router = APIRouter(
    prefix="/auth",
    tags=[
        "authentication",
    ],
)


@router.post(
    "/register",
    response_model=RegistrationApiResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_identity(
    request: RegistrationApiRequest,
    service: RegistrationApiService = Depends(
        get_registration_api_service
    ),
) -> RegistrationApiResponse:
    try:
        result = await service.register(
            RegistrationCommand(
                email=request.email,
                password=request.password,
            )
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail="Registration could not be completed",
        ) from exc

    if not isinstance(
        result,
        RegisteredIdentity,
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail="Registration could not be completed",
        )

    return RegistrationApiResponse()


@router.post(
    "/login",
    response_model=LoginTokenApiResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def login_identity(
    request: LoginApiRequest,
    service: LoginApiService = Depends(
        get_login_api_service
    ),
) -> LoginTokenApiResponse:
    try:
        result = await service.login(
            LoginCommand(
                email=request.email,
                password=request.password,
            )
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Invalid authentication credentials",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from exc

    if not isinstance(
        result,
        AuthenticationTokenPair,
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Invalid authentication credentials",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if (
        not result.access_token
        or not result.refresh_token
        or result.access_token
        == result.refresh_token
        or result.token_type.lower()
        != "bearer"
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Invalid authentication credentials",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return LoginTokenApiResponse(
        token_type=result.token_type,
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        password_change_required=(
            True
            if result.password_change_required
            else None
        ),
    )


@router.post(
    "/change-required-password",
    response_model=ChangeRequiredPasswordApiResponse,
    status_code=status.HTTP_200_OK,
)
async def change_required_password(
    request: ChangeRequiredPasswordApiRequest,
    principal=Depends(
        require_authenticated_principal
    ),
    service: RequiredPasswordChangeService = Depends(
        get_required_password_change_service
    ),
) -> ChangeRequiredPasswordApiResponse:
    subject = getattr(
        principal,
        "subject",
        None,
    )

    if not isinstance(
        subject,
        str,
    ) or not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    try:
        result = await service.replace_required_password(
            user_id=subject,
            current_password=request.current_password,
            new_password=request.new_password,
        )

    except PasswordChangeRejectedError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password replacement was rejected",
        ) from exc

    return ChangeRequiredPasswordApiResponse(
        revoked_sessions=result.revoked_sessions
    )


@router.post(
    "/refresh",
    response_model=SessionTokenApiResponse,
    status_code=status.HTTP_200_OK,
)
async def refresh_session(
    request: RefreshTokenApiRequest,
    service: SessionLifecycleApiService = Depends(
        get_session_lifecycle_api_service
    ),
) -> SessionTokenApiResponse:
    try:
        result = await service.refresh(
            refresh_token=request.refresh_token
        )

    except SessionLifecycleRejectedError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh session",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh session",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from exc

    if not isinstance(
        result,
        AuthenticationTokenPair,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh session",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if (
        not result.access_token
        or not result.refresh_token
        or result.access_token
        == result.refresh_token
        or result.token_type.lower()
        != "bearer"
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh session",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return SessionTokenApiResponse(
        token_type=result.token_type,
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )


@router.post(
    "/logout",
    response_model=SessionActionApiResponse,
    status_code=status.HTTP_200_OK,
)
async def logout_session(
    request: LogoutApiRequest,
    service: SessionLifecycleService = Depends(
        get_session_lifecycle_api_service
    ),
    access_principal: Any | None = Depends(
        optional_logout_access_principal
    ),
) -> SessionActionApiResponse:
    try:
        access_issued_at = None
        access_expires_at = None

        if access_principal is not None:
            issued_at = getattr(
                access_principal,
                "issued_at",
                None,
            )

            expires_at = getattr(
                access_principal,
                "expires_at",
                None,
            )

            if (
                isinstance(issued_at, int)
                and isinstance(expires_at, int)
            ):
                access_issued_at = (
                    datetime.fromtimestamp(
                        issued_at,
                        tz=UTC,
                    )
                )

                access_expires_at = (
                    datetime.fromtimestamp(
                        expires_at,
                        tz=UTC,
                    )
                )

        if access_principal is None:
            await service.logout(
                refresh_token=request.refresh_token,
            )
        else:
            await service.logout(
                refresh_token=request.refresh_token,
                access_token_id=(
                    access_principal.token_id
                ),
                access_user_id=(
                    access_principal.subject
                ),
                access_issued_at=access_issued_at,
                access_expires_at=access_expires_at,
            )

    except SessionLifecycleRejectedError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session logout was rejected",
        ) from exc

    return SessionActionApiResponse(
        status="logged_out"
    )


@router.post(
    "/logout-all",
    response_model=LogoutAllApiResponse,
    status_code=status.HTTP_200_OK,
)
async def logout_all_sessions(
    principal=Depends(
        require_authenticated_principal
    ),
    service: SessionLifecycleApiService = Depends(
        get_session_lifecycle_api_service
    ),
) -> LogoutAllApiResponse:
    subject = getattr(
        principal,
        "subject",
        None,
    )

    if not isinstance(
        subject,
        str,
    ) or not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    try:
        revoked = await service.logout_all(
            user_id=subject
        )

    except SessionLifecycleRejectedError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session revocation could not be completed",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session revocation could not be completed",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from exc

    return LogoutAllApiResponse(
        revoked_sessions=revoked
    )

# New endpoint for introspection
@router.get(
    "/introspection",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
async def session_introspection(
    principal=Depends(require_authenticated_principal),
    session_repo: IdentityUserRepository = Depends(get_session_repository),
):
    return await get_session_introspection(principal.subject, session_repo)
