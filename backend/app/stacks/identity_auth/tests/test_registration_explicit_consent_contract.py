from __future__ import annotations

import pytest

from backend.app.stacks.identity_auth.service_contracts import (
    RegistrationCommand,
)

VERSION = "neurovest-beta-terms-2026-10-09-v1"


def test_missing_both_consent_fields_is_rejected():
    with pytest.raises(TypeError):
        RegistrationCommand(
            email="test@example.invalid",
            password="long-enough-password",
        )


def test_missing_acceptance_flag_is_rejected():
    with pytest.raises(TypeError):
        RegistrationCommand(
            email="test@example.invalid",
            password="long-enough-password",
            terms_version=VERSION,
        )


def test_missing_terms_version_is_rejected():
    with pytest.raises(TypeError):
        RegistrationCommand(
            email="test@example.invalid",
            password="long-enough-password",
            terms_accepted=True,
        )


def test_explicit_consent_fields_are_preserved():
    command = RegistrationCommand(
        email="test@example.invalid",
        password="long-enough-password",
        terms_accepted=True,
        terms_version=VERSION,
    )

    assert command.terms_accepted is True
    assert command.terms_version == VERSION


def test_explicit_rejection_remains_representable():
    command = RegistrationCommand(
        email="test@example.invalid",
        password="long-enough-password",
        terms_accepted=False,
        terms_version=VERSION,
    )

    assert command.terms_accepted is False
