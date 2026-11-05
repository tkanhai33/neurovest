from types import SimpleNamespace

from backend.app.stacks.chat_public import chat_runtime
from backend.app.stacks.chat_public.weather_tools.live_weather import (
    LiveWeather,
    extract_weather_location,
)


def test_extract_weather_location_from_normal_question() -> None:
    assert (
        extract_weather_location(
            "What's the weather like in Edmonton, AB?"
        )
        == "Edmonton, AB"
    )


def test_live_weather_is_direct_and_grounded(
    monkeypatch,
) -> None:
    weather = LiveWeather(
        name="Edmonton",
        admin1="Alberta",
        country="Canada",
        timezone="America/Edmonton",
        observed_at="2026-09-23T18:00",
        temperature_c=16.3,
        feels_like_c=14.4,
        humidity_percent=52.0,
        precipitation_mm=0.0,
        weather_code=3,
        wind_kmh=7.2,
        today_high_c=17.1,
        today_low_c=6.8,
        today_precipitation_probability_percent=10.0,
    )

    monkeypatch.setattr(
        chat_runtime,
        "fetch_live_weather",
        lambda location, use_cache: weather,
    )

    intent = SimpleNamespace(
        blocked=False,
        intent="trading_conversation",
        symbol=None,
    )

    result = chat_runtime.handle_chat_message(
        "What's the weather like in Edmonton, AB?",
        detected_intent=intent,
    )

    message = result["response"]["message"]

    assert result["status"] == "ok"
    assert result["provider"] == "open_meteo_weather"
    assert result["model"] is None
    assert result["tool_truth_state"] == "grounded"
    assert "Edmonton, Alberta, Canada" in message
    assert "Overcast" in message
    assert "Temperature: 16.3 °C" in message
    assert "no order was created" not in message


def test_extract_temp_location_with_current_time_words() -> None:
    assert (
        extract_weather_location(
            "whats the temp in edmonton right now?"
        )
        == "edmonton"
    )
