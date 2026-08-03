from pathlib import Path
import re


COOKIE_FILE = Path(
    "frontend/lib/sessionCookies.ts"
)


def source() -> str:
    return COOKIE_FILE.read_text(
        encoding="utf-8"
    )


def test_cookie_policy_has_explicit_local_override():
    text = source()

    assert (
        'process.env.NEUROVEST_COOKIE_SECURE === "false"'
        in text
    )


def test_production_remains_secure_by_default():
    text = source()

    assert (
        'process.env.NODE_ENV === "production"'
        in text
    )

    assert (
        'process.env.NEUROVEST_COOKIE_SECURE === "false"'
        in text
    )


def test_both_cookie_option_groups_use_policy():
    text = source()

    matches = re.findall(
        r"secure\s*:\s*secureBrowserCookies",
        text,
    )

    assert len(matches) == 2


def test_old_is_production_binding_is_removed():
    text = source()

    assert "const isProduction =" not in text
    assert "secure: isProduction" not in text


def test_no_unconditional_insecure_cookie_setting():
    text = source()

    assert not re.search(
        r"secure\s*:\s*false\b",
        text,
    )


def test_cookie_policy_name_is_present():
    text = source()

    assert (
        "const secureBrowserCookies ="
        in text
    )
