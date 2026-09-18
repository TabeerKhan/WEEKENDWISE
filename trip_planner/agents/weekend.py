"""Deterministic Demo Mode agents for the WeekendWise workflow."""

from __future__ import annotations

from datetime import date, timedelta

from trip_planner.agents._base import days, event
from trip_planner.config import DEMO_MODE


def _demo_weather(state: dict) -> list[dict]:
    return [{
        "date": day,
        "condition": "Partly cloudy",
        "rain_chance": 20,
        "temperature_c": 29,
        "outdoor_score": 90,
        "source": "demo",
    } for day in _dates(state)]


def _dates(state: dict) -> list[str]:
    start = date.fromisoformat(state["start_date"])
    return [(start + timedelta(days=index)).isoformat() for index in range(days(state))]


def master_planner(state: dict) -> dict:
    destination = state.get("destination", "").strip()
    errors = []
    if not destination:
        errors.append("Destination is required.")
    if days(state) not in (1, 2, 3):
        errors.append("WeekendWise supports trips of 1 to 3 days.")
    if state.get("travelers", 0) < 1:
        errors.append("Travelers must be at least 1.")
    if state.get("budget_inr", 0) <= 0:
        errors.append("Budget must be greater than zero.")
    return {
        "destination": destination,
        "errors": errors,
        **event("Master Planner", "complete" if not errors else "failed", "Requirements understood", state),
    }


def weather_agent(state: dict) -> dict:
    if not state.get("demo_mode", DEMO_MODE):
        try:
            from trip_planner.adapters.weather import fetch_weather

            weather = fetch_weather(state["destination"], state["start_date"], state["end_date"])
            return {"weather": weather, **event("Weather Agent", "complete", "Weather checked (OpenWeatherMap)", state)}
        except Exception as exc:
            weather = _demo_weather(state)
            return {"weather": weather, "errors": [f"Weather API unavailable; using Demo Mode: {exc}"], **event("Weather Agent", "warning", "Live weather unavailable; Demo Mode fallback", state)}
    weather = _demo_weather(state)
    return {"weather": weather, **event("Weather Agent", "complete", "Weather checked (Demo Mode)", state)}


def event_agent(state: dict) -> dict:
    dates = _dates(state)
    events = [{
        "name": "Vizag Sunset Music Evening",
        "venue": "Beach Road Amphitheatre",
        "location": "Beach Road",
        "date": dates[-1] if dates else state.get("start_date", ""),
        "start_time": "19:00",
        "end_time": "21:00",
        "cost_inr": 300,
        "category": "Events",
        "description": "A low-cost evening cultural event.",
        "source": "demo",
    }]
    return {"events": events, **event("Event Finder", "complete", "Events found (Demo Mode)", state)}


def activity_agent(state: dict) -> dict:
    activities = [
        {"name": "Beach Morning", "category": "Beaches", "location": "Ramakrishna Beach", "duration_minutes": 120, "cost_inr": 0, "opening_hours": "05:00-22:00", "description": "Relaxed beach walk and photography.", "source": "demo"},
        {"name": "Kailasagiri Viewpoint", "category": "Nature", "location": "Kailasagiri", "duration_minutes": 150, "cost_inr": 200, "opening_hours": "09:00-20:00", "description": "Hilltop views and light sightseeing.", "source": "demo"},
        {"name": "Submarine Museum", "category": "History", "location": "RK Beach", "duration_minutes": 90, "cost_inr": 100, "opening_hours": "10:00-17:00", "description": "Compact local history attraction.", "source": "demo"},
    ]
    return {"activities": activities, **event("Activity Agent", "complete", "Attractions found (Demo Mode)", state)}


def restaurant_agent(state: dict) -> dict:
    restaurants = [
        {"name": "Harbour Thali House", "cuisine": "Local", "location": "Beach Road", "meal": "Lunch", "cost_inr": 450, "opening_hours": "11:00-16:00", "description": "Affordable local thali for the group.", "source": "demo"},
        {"name": "Seaside Tiffin Corner", "cuisine": "South Indian", "location": "RK Beach", "meal": "Dinner", "cost_inr": 350, "opening_hours": "18:00-22:00", "description": "Quick, budget-friendly dinner.", "source": "demo"},
    ]
    return {"restaurants": restaurants, **event("Restaurant Agent", "complete", "Restaurants found (Demo Mode)", state)}


def route_agent(state: dict) -> dict:
    mode = state.get("transport_preference") or "Local taxi"
    legs = [
        {"from_location": "Weekend base", "to_location": "Ramakrishna Beach", "mode": mode, "distance_km": 4.0, "travel_minutes": 20, "cost_inr": 250},
        {"from_location": "Ramakrishna Beach", "to_location": "Kailasagiri", "mode": mode, "distance_km": 7.0, "travel_minutes": 30, "cost_inr": 350},
        {"from_location": "Kailasagiri", "to_location": "Beach Road", "mode": mode, "distance_km": 8.0, "travel_minutes": 35, "cost_inr": 300},
    ]
    route = {"stops": ["Weekend base", "Ramakrishna Beach", "Kailasagiri", "Beach Road", "Weekend base"], "legs": legs, "total_distance_km": 19.0, "total_travel_minutes": 85, "transport_method": mode, "transport_cost_inr": 900, "source": "demo"}
    return {"route": route, **event("Route Agent", "complete", "Route optimized (Demo Mode)", state)}


def _make_itinerary(state: dict) -> list[dict]:
    dates = _dates(state)
    second = dates[1] if len(dates) > 1 else dates[0]
    return [
        {"date": dates[0], "time": "09:00", "title": "Beach Morning", "category": "Beaches", "location": "Ramakrishna Beach", "duration_minutes": 120, "cost_inr": 0, "travel_minutes": 20, "reason": "Scheduled early for comfortable outdoor weather."},
        {"date": dates[0], "time": "12:30", "title": "Local Thali Lunch", "category": "Food", "location": "Beach Road", "duration_minutes": 60, "cost_inr": 450, "travel_minutes": 15, "reason": "Affordable local food close to the morning route."},
        {"date": dates[0], "time": "15:00", "title": "Kailasagiri Viewpoint", "category": "Nature", "location": "Kailasagiri", "duration_minutes": 150, "cost_inr": 200, "travel_minutes": 30, "reason": "A compact attraction that fits the afternoon window."},
        {"date": second, "time": "10:00", "title": "Submarine Museum", "category": "History", "location": "RK Beach", "duration_minutes": 90, "cost_inr": 100, "travel_minutes": 25, "reason": "Indoor alternative with a short visit duration."},
        {"date": second, "time": "19:00", "title": "Sunset Music Evening", "category": "Events", "location": "Beach Road Amphitheatre", "duration_minutes": 120, "cost_inr": 300, "travel_minutes": 20, "reason": "Matches the event preference and evening timing."},
    ]


def master_itinerary(state: dict) -> dict:
    itinerary = _make_itinerary(state)
    if state.get("replan_count", 0) > 0:
        itinerary = [item for item in itinerary if item["title"] != "Kailasagiri Viewpoint"]
        itinerary.append({"date": _dates(state)[-1], "time": "15:00", "title": "Free Beach Walk", "category": "Relaxation", "location": "Ramakrishna Beach", "duration_minutes": 90, "cost_inr": 0, "travel_minutes": 10, "reason": "Lower-cost alternative requested by the Budget Agent."})
    return {"itinerary": itinerary, **event("Master Planner", "complete", "Initial itinerary created" if not state.get("replan_count") else "Alternatives requested and itinerary regenerated", state)}


def budget_agent(state: dict) -> dict:
    travelers = max(int(state.get("travelers", 1)), 1)
    food = sum(item.get("cost_inr", 0) for item in state.get("restaurants", [])) * travelers
    activities = sum(item.get("cost_inr", 0) for item in state.get("itinerary", []) if item.get("category") not in {"Food", "Events"}) * travelers
    events = sum(item.get("cost_inr", 0) for item in state.get("events", [])) * travelers
    transport = state.get("route", {}).get("transport_cost_inr", 0)
    miscellaneous = 500
    total = food + activities + events + transport + miscellaneous
    if state.get("replan_count", 0) == 0 and state.get("demo_mode", True):
        total += 4500
        miscellaneous += 4500
    breakdown = {"Food": food, "Transport": transport, "Activities": activities, "Events": events, "Miscellaneous": miscellaneous, "total": total, "budget": state.get("budget_inr", 0), "remaining": state.get("budget_inr", 0) - total}
    status = "warning" if total > state.get("budget_inr", 0) else "complete"
    message = "Initial plan exceeds budget" if status == "warning" else "Budget constraint satisfied"
    return {"budget_breakdown": breakdown, **event("Budget Agent", status, message, state)}


def validator_agent(state: dict) -> dict:
    budget = state.get("budget_breakdown", {})
    issues = []
    recommendations = []
    if budget.get("total", 0) > state.get("budget_inr", 0):
        issues.append(f"Budget exceeds limit by {budget['total'] - state.get('budget_inr', 0):.0f} INR.")
        recommendations.append("Use lower-cost food, activity, and transport alternatives.")
    if state.get("route", {}).get("total_travel_minutes", 0) > 180:
        issues.append("Route contains excessive travel time.")
        recommendations.append("Group activities by nearby locations.")
    titles = [item.get("title") for item in state.get("itinerary", [])]
    if len(titles) != len(set(titles)):
        issues.append("Itinerary contains duplicate activities.")
    result = {"status": "FAIL" if issues else "PASS", "issues": issues, "recommendations": recommendations}
    status = "failed" if issues else "complete"
    message = issues[0] if issues else "Final itinerary validated"
    return {"validation": result, "validation_history": [result], "replan_issues": issues, **event("Validator", status, message, state)}
