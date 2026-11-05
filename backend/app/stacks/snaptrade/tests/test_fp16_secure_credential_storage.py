from __future__ import annotations

import ast
from pathlib import Path

import pytest
from cryptography.fernet import Fernet

from backend.app.stacks.snaptrade.security.user_secret_cipher import (
    SnapTradeSecretConfigurationError,
    decrypt_snaptrade_user_secret,
    encrypt_snaptrade_user_secret,
    load_snaptrade_user_secret_cipher,
)


ROOT = Path(__file__).resolve().parents[5]

MODEL = (
    ROOT
    / "backend/app/stacks/snaptrade/persistence/"
    "credential_models.py"
)

REPOSITORY = (
    ROOT
    / "backend/app/stacks/snaptrade/persistence/"
    "credential_repository.py"
)

REGISTRY = (
    ROOT
    / "backend/app/stacks/db_runtime/model_registry.py"
)


def read(path: Path) -> str:
    assert path.exists(), (
        f"Missing required file: {path}"
    )

    return path.read_text(
        encoding="utf-8",
        errors="ignore",
    )


def test_user_secret_round_trip_is_encrypted() -> None:
    cipher = Fernet(
        Fernet.generate_key()
    )

    plaintext = (
        "snaptrade-user-secret-example"
    )

    ciphertext = (
        encrypt_snaptrade_user_secret(
            plaintext,
            cipher=cipher,
        )
    )

    assert isinstance(
        ciphertext,
        bytes,
    )

    assert plaintext.encode(
        "utf-8"
    ) not in ciphertext

    assert (
        decrypt_snaptrade_user_secret(
            ciphertext,
            cipher=cipher,
        )
        == plaintext
    )


def test_missing_encryption_key_fails_closed() -> None:
    with pytest.raises(
        SnapTradeSecretConfigurationError
    ):
        load_snaptrade_user_secret_cipher(
            environ={}
        )


def test_model_persists_ciphertext_not_plaintext_secret() -> None:
    text = read(
        MODEL
    )

    assert "encrypted_user_secret" in text
    assert "LargeBinary" in text
    assert "snaptrade_user_id" in text
    assert "neurovest_user_id" in text

    tree = ast.parse(
        text
    )

    assigned_names = {
        node.target.id
        for node in ast.walk(tree)
        if isinstance(
            node,
            ast.AnnAssign,
        )
        and isinstance(
            node.target,
            ast.Name,
        )
    }

    assert "user_secret" not in assigned_names
    assert (
        "encrypted_user_secret"
        in assigned_names
    )


def test_repository_is_owner_scoped() -> None:
    text = read(
        REPOSITORY
    )

    assert "neurovest_user_id" in text
    assert "get_for_owner" in text
    assert (
        "store_registered_credential"
        in text
    )

    assert (
        "load_provider_identity"
        in text
    )


def test_safe_serializer_excludes_secret_material() -> None:
    text = read(
        REPOSITORY
    )

    serializer_start = text.index(
        "def serialize_snaptrade_credential_state"
    )

    serializer = text[
        serializer_start:
    ]

    assert (
        '"user_secret_exposed": False'
        in serializer
    )

    assert (
        '"ciphertext_exposed": False'
        in serializer
    )

    assert (
        '"encrypted_user_secret"'
        not in serializer
    )


def test_snaptrade_model_is_registered() -> None:
    text = read(
        REGISTRY
    )

    assert (
        "snaptrade_credential_models"
        in text
    )


def test_snaptrade_model_is_returned_by_runtime_registry() -> None:
    import ast

    text = read(
        REGISTRY
    )

    tree = ast.parse(
        text
    )

    function = next(
        node
        for node in tree.body
        if isinstance(
            node,
            ast.FunctionDef,
        )
        and node.name
        == "register_runtime_models"
    )

    return_node = next(
        node
        for node in ast.walk(
            function
        )
        if isinstance(
            node,
            ast.Return,
        )
    )

    assert isinstance(
        return_node.value,
        ast.Tuple,
    )

    returned_names = {
        element.id
        for element in return_node.value.elts
        if isinstance(
            element,
            ast.Name,
        )
    }

    assert (
        "snaptrade_credential_models"
        in returned_names
    )


def test_registered_metadata_contains_snaptrade_table() -> None:
    from backend.app.stacks.db_runtime.database import (
        Base,
    )
    from backend.app.stacks.db_runtime.model_registry import (
        register_runtime_models,
    )

    registered = register_runtime_models()

    assert any(
        module.__name__.endswith(
            "credential_models"
        )
        for module in registered
    )

    assert (
        "snaptrade_user_credentials"
        in Base.metadata.tables
    )
