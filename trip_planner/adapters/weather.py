"""OpenWeatherMap adapter with explicit source metadata."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any

import requests

from trip_planner.config import OPENWEATHERMAP_API_KEY

_GEOCODE_URL = "https://api.openweathermap.org/geo/1.0/direct"
_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


def fetch_weather(destination: str, start_date: str, end_date: str) -> list[dict[str, Any]]:
    """Fetch daily weather for the requested dates from OpenWeatherMap.

    OpenWeatherMap's free forecast endpoint covers roughly five days. A
    RuntimeError is raised for missing configuration or unavailable data so the
    caller can choose a clearly labelled Demo Mode fallback.
    """
    if not OPENWEATHERMAP_API_KEY:
        raise RuntimeError("OPENWEATHERMAP_API_KEY is not configured")

    location = _request_json(
        _GEOCODE_URL,
        {"q": destination, "limit": 1, "appid": OPENWEATHERMAP_API_KEY},
    )
    if not location:
        raise RuntimeError(f"Could not geocode destination: {destination}")

    latitude = location[0].get("lat")
    longitude = location[0].get("lon")
    if latitude is None or longitude is None:
        raise RuntimeError("Geocoding response did not include coordinates")

    forecast = _request_json(
        _FORECAST_URL,
        {
            "lat": latitude,
            "lon": longitude,
            "appid": OPENWEATHERMAP_API_KEY,
            "units": "metric",
        },
    )
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in forecast.get("list", []):
        day = item.get("dt_txt", "").split(" ", 1)[0]
        if day:
            grouped[day].append(item)

    requested_days = _date_range(start_date, end_date)
    result = []
    for day in requested_days:
        slots = grouped.get(day, [])
        if not slots:
            raise RuntimeError(f"Weather forecast is unavailable for {day}")
        rain_values = [float(slot.get("pop", 0)) for slot in slots]
        temperatures = [float(slot.get("main", {}).get("temp", 0)) for slot in slots]
        rain_chance = round(max(rain_values, default=0) * 100)
        condition = _most_common_condition(slots)
        result.append({
            "date": day,
            "condition": condition,
            "rain_chance": rain_chance,
            "temperature_c": round(sum(temperatures) / len(temperatures), 1),
            "outdoor_score": max(0, min(100, 100 - rain_chance)),
            "source": "openweathermap",
        })
    return result


def _request_json(url: str, params: dict[str, Any]) -> dict[str, Any] | list:
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def _date_range(start_date: str, end_date: str) -> list[str]:
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    return [(start.fromordinal(day)).isoformat() for day in range(start.toordinal(), end.toordinal() + 1)]


def _most_common_condition(slots: list[dict[str, Any]]) -> str:
    descriptions = [
        slot.get("weather", [{}])[0].get("description", "Unknown")
        for slot in slots
    ]
    return max(set(descriptions), key=descriptions.count).title() if descriptions else "Unknown"
