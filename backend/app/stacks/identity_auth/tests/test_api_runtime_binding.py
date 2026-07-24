from __future__ import annotations

import inspect

from backend.app.stacks.identity_auth import (
    api_dependencies,
)

from backend.app.stacks.identity_auth.login_service import (
    LoginService,
)

from backend.app.stacks.identity_auth.registration_service import (
    RegistrationService,
)


def test_registration_dependency_is_async_generator() -> None:
    assert inspect.isasyncgenfunction(
        api_dependencies.get_registration_api_service
    )


def test_login_dependency_is_async_generator() -> None:
    assert inspect.isasyncgenfunction(
        api_dependencies.get_login_api_service
    )


def test_registration_dependency_contract_annotation() -> None:
    annotation = inspect.signature(
        api_dependencies.get_registration_api_service
    ).return_annotation

    assert annotation is not None


def test_login_dependency_contract_annotation() -> None:
    annotation = inspect.signature(
        api_dependencies.get_login_api_service
    ).return_annotation

    assert annotation is not None


def test_runtime_service_types_are_canonical() -> None:
    assert RegistrationService.__module__ == (
        "backend.app.stacks.identity_auth."
        "registration_service"
    )

    assert LoginService.__module__ == (
        "backend.app.stacks.identity_auth."
        "login_service"
    )
