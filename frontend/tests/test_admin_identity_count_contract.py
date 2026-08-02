from pathlib import Path


ROUTER = Path(
    "backend/app/stacks/identity_auth/"
    "admin_read_router.py"
)

MODELS = Path(
    "backend/app/stacks/identity_auth/"
    "admin_read_models.py"
)

API_MODELS = Path(
    "backend/app/stacks/identity_auth/"
    "admin_read_api_models.py"
)

MAIN = Path(
    "backend/app/main.py"
)

USERS_PAGE = Path(
    "frontend/app/admin/users/page.tsx"
)

STATS_PAGE = Path(
    "frontend/app/admin/user-stats/page.tsx"
)


def test_user_list_no_longer_stops_at_fifty() -> None:
    source = ROUTER.read_text(
        encoding="utf-8",
    )

    function = source[
        source.index(
            "async def list_administrative_users("
        ):
        source.index(
            "@router.get(",
            source.index(
                "async def list_administrative_users("
            ),
        )
    ]

    assert "default=500" in function
    assert "le=500" in function
    assert "default=50," not in function


def test_user_list_response_has_total() -> None:
    source = API_MODELS.read_text(
        encoding="utf-8",
    )

    section = source[
        source.index(
            "class AdministrativeUserListResponse"
        ):
        source.index(
            "class ",
            source.index(
                "class AdministrativeUserListResponse"
            )
            + 10,
        )
    ]

    assert "total: int = Field(" in section
    assert "le=500" in section


def test_user_list_service_counts_all_users() -> None:
    source = MODELS.read_text(
        encoding="utf-8",
    )

    assert "func.count()" in source
    assert ".select_from(" in source
    assert "total_result.scalar_one()" in source
    assert "total=total," in source


def test_user_operations_requests_complete_list() -> None:
    source = USERS_PAGE.read_text(
        encoding="utf-8",
    )

    assert (
        '"/api/admin/users?offset=0&limit=500"'
        in source
    )

    assert "total: number;" in source


def test_statistics_separate_identity_categories() -> None:
    source = MAIN.read_text(
        encoding="utf-8",
    )

    assert "qualification_test_accounts =" in source
    assert "customer_accounts =" in source
    assert "internal_accounts =" in source

    assert (
        '"qualification_test_accounts":'
        in source
    )

    assert (
        '"customer_accounts": customer_accounts'
        in source
    )

    assert (
        '"internal_accounts": internal_accounts'
        in source
    )


def test_statistics_page_labels_customer_counts() -> None:
    source = STATS_PAGE.read_text(
        encoding="utf-8",
    )

    assert 'label="Customer accounts"' in source

    assert (
        "statistics.users.customer_accounts"
        in source
    )

    assert (
        "Qualification / test identities"
        in source
    )

    assert (
        "statistics.users"
        ".qualification_test_accounts"
        in source.replace(
            "\n",
            "",
        ).replace(
            " ",
            "",
        )
        or (
            "qualification_test_accounts"
            in source
        )
    )

    assert "Database identities" in source
    assert "Internal accounts" in source
