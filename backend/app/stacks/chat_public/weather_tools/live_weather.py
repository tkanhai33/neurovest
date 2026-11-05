"""
Read-only current weather for normal city-based chat questions.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import json
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


_CACHE_TTL = timedelta(minutes=5)

_GEOCODING_URL = (
    "https://geocoding-api.open-meteo.com/v1/search"
)

_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

_LOCATION_MARKERS = (
    "weather like in ",
    "weather in ",
    "weather for ",
    "weather at ",
    "forecast in ",
    "forecast for ",
    "forecast at ",
    "temperature in ",
    "temperature for ",
    "temperature at ",
    "temp in ",
    "temp for ",
    "temp at ",
    "conditions in ",
    "conditions for ",
    "raining in ",
    "raining at ",
    "snowing in ",
    "snowing at ",
)

_WEATHER_DESCRIPTIONS = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


@dataclass(frozen=True, slots=True)
class LiveWeather:
    name: str
    admin1: str | None
    country: str | None
    timezone: str
    observed_at: str
    temperature_c: float | None
    feels_like_c: float | None
    humidity_percent: float | None
    precipitation_mm: float | None
    weather_code: int | None
    wind_kmh: float | None
    today_high_c: float | None
    today_low_c: float | None
    today_precipitation_probability_percent: float | None


_cached_at: dict[str, datetime] = {}
_cached_weather: dict[str, LiveWeather] = {}


def extract_weather_location(message: str) -> str | None:
    source = str(message or "").strip()
    lowered = source.casefold()

    for marker in _LOCATION_MARKERS:
        position = lowered.find(marker)

        if position < 0:
            continue

        location = source[
            position + len(marker):
        ].strip(" .,!?:;\n\t")

        lowered_location = location.casefold()

        for suffix in (
            " right now",
            " currently",
            " today",
            " now",
        ):
            if lowered_location.endswith(suffix):
                location = location[
                    : -len(suffix)
                ].strip(" .,!?:;\n\t")
                break

        if location:
            return location

    return None


def weather_description(weather_code: int | None) -> str:
    if weather_code is None:
        return "Conditions unavailable"

    return _WEATHER_DESCRIPTIONS.get(
        weather_code,
        f"Weather code {weather_code}",
    )


def _fetch_json(
    url: str,
    params: dict[str, Any],
) -> dict[str, Any]:
    request = Request(
        url + "?" + urlencode(params),
        headers={
            "Accept": "application/json",
            "User-Agent": "NeuroVestLiveWeather/1.0",
        },
    )

    with urlopen(request, timeout=20) as response:
        return json.loads(
            response.read().decode("utf-8")
        )


def _optional_float(
    values: dict[str, Any],
    key: str,
) -> float | None:
    value = values.get(key)

    if value is None:
        return None

    return float(value)


def _first_daily_float(
    daily: dict[str, Any],
    key: str,
) -> float | None:
    values = daily.get(key) or []

    if not values or values[0] is None:
        return None

    return float(values[0])


def fetch_live_weather(
    location: str,
    *,
    use_cache: bool = True,
) -> LiveWeather:
    requested_location = str(location or "").strip()

    if not requested_location:
        raise ValueError("A city or location is required.")

    cache_key = requested_location.casefold()
    now = datetime.now(UTC)

    if (
        use_cache
        and cache_key in _cached_at
        and cache_key in _cached_weather
        and now - _cached_at[cache_key] <= _CACHE_TTL
    ):
        return _cached_weather[cache_key]

    geocoding = _fetch_json(
        _GEOCODING_URL,
        {
            "name": requested_location,
            "count": 5,
            "language": "en",
            "format": "json",
        },
    )

    matches = geocoding.get("results") or []

    if not matches:
        raise LookupError(
            "No matching city or location was found."
        )

    selected = matches[0]

    forecast = _fetch_json(
        _FORECAST_URL,
        {
            "latitude": selected["latitude"],
            "longitude": selected["longitude"],
            "timezone": "auto",
            "current": (
                "temperature_2m,relative_humidity_2m,"
                "apparent_temperature,precipitation,"
                "weather_code,wind_speed_10m"
            ),
            "daily": (
                "temperature_2m_max,temperature_2m_min,"
                "precipitation_probability_max"
            ),
            "forecast_days": 1,
        },
    )

    current = forecast.get("current") or {}
    daily = forecast.get("daily") or {}
    code = current.get("weather_code")

    result = LiveWeather(
        name=str(selected.get("name") or requested_location),
        admin1=(
            str(selected["admin1"])
            if selected.get("admin1")
            else None
        ),
        country=(
            str(selected["country"])
            if selected.get("country")
            else None
        ),
        timezone=str(forecast.get("timezone") or "UTC"),
        observed_at=str(current.get("time") or ""),
        temperature_c=_optional_float(
            current,
            "temperature_2m",
        ),
        feels_like_c=_optional_float(
            current,
            "apparent_temperature",
        ),
        humidity_percent=_optional_float(
            current,
            "relative_humidity_2m",
        ),
        precipitation_mm=_optional_float(
            current,
            "precipitation",
        ),
        weather_code=(
            int(code)
            if code is not None
            else None
        ),
        wind_kmh=_optional_float(
            current,
            "wind_speed_10m",
        ),
        today_high_c=_first_daily_float(
            daily,
            "temperature_2m_max",
        ),
        today_low_c=_first_daily_float(
            daily,
            "temperature_2m_min",
        ),
        today_precipitation_probability_percent=(
            _first_daily_float(
                daily,
                "precipitation_probability_max",
            )
        ),
    )

    _cached_at[cache_key] = now
    _cached_weather[cache_key] = result

    return result


__all__ = [
    "LiveWeather",
    "extract_weather_location",
    "fetch_live_weather",
    "weather_description",
]
