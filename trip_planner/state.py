"""Shared state and typed records for WeekendWise."""

from __future__ import annotations

from typing import Annotated, Any, Optional
from typing_extensions import TypedDict


def _append(existing: list, new: list) -> list:
    return (existing or []) + (new or [])


class ActivityOption(TypedDict, total=False):
    name: str
    category: str
    location: str
    duration_minutes: int
    cost_inr: float
    opening_hours: str
    description: str
    source: str


class EventOption(TypedDict, total=False):
    name: str
    venue: str
    location: str
    date: str
    start_time: str
    end_time: str
    cost_inr: float
    category: str
    description: str
    source: str


class RestaurantOption(TypedDict, total=False):
    name: str
    cuisine: str
    location: str
    meal: str
    cost_inr: float
    opening_hours: str
    description: str
    source: str


class WeatherDay(TypedDict, total=False):
    date: str
    condition: str
    rain_chance: int
    temperature_c: float
    outdoor_score: int
    source: str


class ItineraryItem(TypedDict, total=False):
    date: str
    time: str
    title: str
    category: str
    location: str
    duration_minutes: int
    cost_inr: float
    travel_minutes: int
    reason: str


class ValidationResult(TypedDict):
    status: str
    issues: list[str]
    recommendations: list[str]


class AgentEvent(TypedDict, total=False):
    agent: str
    status: str
    message: str
    attempt: int


class WeekendState(TypedDict, total=False):
    destination: str
    start_date: str
    end_date: str
    travelers: int
    budget_inr: float
    transport_preference: str
    interests: list[str]
    accommodation_name: str
    demo_mode: bool
    max_replans: int
    replan_count: int
    replan_issues: list[str]
    weather: list[WeatherDay]
    events: list[EventOption]
    activities: list[ActivityOption]
    restaurants: list[RestaurantOption]
    route: dict[str, Any]
    itinerary: list[ItineraryItem]
    budget_breakdown: dict[str, float]
    validation: ValidationResult
    validation_history: list[ValidationResult]
    execution_trace: Annotated[list[AgentEvent], _append]
    errors: Annotated[list[str], _append]
    final_plan: Optional[dict[str, Any]]


TripState = WeekendState
