from datetime import UTC, datetime
from types import SimpleNamespace

from backend.app.stacks.chat_public import chat_runtime
from backend.app.stacks.news_intelligence.official_economic_feeds import (
    OfficialEconomicRelease,
)


def test_current_canadian_economic_releases_are_direct_and_grounded(
    monkeypatch,
) -> None:
    releases = [
        OfficialEconomicRelease(
            title="Consumer Price Index, August 2026",
            issuer="Statistics Canada",
            published_at=datetime(2026, 9, 23, tzinfo=UTC),
            url="https://www.statcan.gc.ca/example",
        ),
        OfficialEconomicRelease(
            title="Bank of Canada policy update",
            issuer="Bank of Canada",
            published_at=datetime(2026, 9, 22, tzinfo=UTC),
            url="https://www.bankofcanada.ca/example",
        ),
    ]

    monkeypatch.setattr(
        chat_runtime,
        "fetch_official_economic_releases",
        lambda *, limit, use_cache: releases[:limit],
    )

    intent = SimpleNamespace(
        blocked=False,
        intent="trading_conversation",
        symbol=None,
    )

    result = chat_runtime.handle_chat_message(
        "What are the latest Canadian economic releases?",
        detected_intent=intent,
    )

    message = result["response"]["message"]

    assert result["status"] == "ok"
    assert result["provider"] == (
        "official_canadian_economic_feeds"
    )
    assert result["model"] is None
    assert result["tool_truth_state"] == "grounded"
    assert "Statistics Canada" in message
    assert "Bank of Canada" in message
    assert "no order was created" in message


def test_economic_title_filter_excludes_demographic_releases() -> None:
    from backend.app.stacks.news_intelligence.official_economic_feeds import (
        OfficialEconomicRelease,
        _is_economic_release,
    )

    timestamp = datetime(2026, 9, 23, tzinfo=UTC)

    assert _is_economic_release(
        OfficialEconomicRelease(
            title="Consumer Price Index, August 2026",
            issuer="Statistics Canada",
            published_at=timestamp,
            url="https://example.test/cpi",
        )
    )

    assert not _is_economic_release(
        OfficialEconomicRelease(
            title="Births, 2025",
            issuer="Statistics Canada",
            published_at=timestamp,
            url="https://example.test/births",
        )
    )

    assert not _is_economic_release(
        OfficialEconomicRelease(
            title="Canada's population estimates, second quarter 2026",
            issuer="Statistics Canada",
            published_at=timestamp,
            url="https://example.test/population",
        )
    )
