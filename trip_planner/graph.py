"""LangGraph workflow for WeekendWise."""

from __future__ import annotations

from datetime import date
from typing import Optional

from langgraph.graph import END, START, StateGraph

from trip_planner.agents import (
    activity_agent,
    budget_agent,
    event_agent,
    master_itinerary,
    master_planner,
    restaurant_agent,
    route_agent,
    validator_agent,
    weather_agent,
)
from trip_planner.config import DEMO_MODE, MAX_REPLANS
from trip_planner.state import WeekendState

RESEARCH_NODES = ["weather_agent", "event_agent", "activity_agent", "restaurant_agent", "route_agent"]


def research_barrier(state: WeekendState) -> dict:
    return {}


def validation_route(state: WeekendState) -> str:
    result = state.get("validation", {})
    if result.get("status") == "PASS":
        return "finalize"
    if state.get("replan_count", 0) >= state.get("max_replans", MAX_REPLANS):
        return "finalize"
    return "replan"


def replan(state: WeekendState) -> dict:
    return {
        "replan_count": state.get("replan_count", 0) + 1,
        "replan_issues": state.get("validation", {}).get("issues", []),
    }


def finalize(state: WeekendState) -> dict:
    validation = state.get("validation", {"status": "FAIL", "issues": ["Validation did not run"], "recommendations": []})
    return {"final_plan": {
        "brand": "WeekendWise",
        "status": validation.get("status", "FAIL"),
        "destination": state.get("destination", ""),
        "days": state.get("itinerary", []),
        "weather": state.get("weather", []),
        "budget": state.get("budget_breakdown", {}),
        "route": state.get("route", {}),
        "validation": validation,
        "replans": state.get("replan_count", 0),
        "demo_mode": state.get("demo_mode", True),
    }}


def build_graph():
    graph = StateGraph(WeekendState)
    graph.add_node("master_planner", master_planner)
    graph.add_node("weather_agent", weather_agent)
    graph.add_node("event_agent", event_agent)
    graph.add_node("activity_agent", activity_agent)
    graph.add_node("restaurant_agent", restaurant_agent)
    graph.add_node("route_agent", route_agent)
    graph.add_node("research_barrier", research_barrier)
    graph.add_node("master_itinerary", master_itinerary)
    graph.add_node("budget_agent", budget_agent)
    graph.add_node("validator_agent", validator_agent)
    graph.add_node("replan", replan)
    graph.add_node("finalize", finalize)

    graph.add_edge(START, "master_planner")
    for node in RESEARCH_NODES:
        graph.add_edge("master_planner", node)
        graph.add_edge(node, "research_barrier")
    graph.add_edge("research_barrier", "master_itinerary")
    graph.add_edge("master_itinerary", "budget_agent")
    graph.add_edge("budget_agent", "validator_agent")
    graph.add_conditional_edges("validator_agent", validation_route, {"replan": "replan", "finalize": "finalize"})
    graph.add_edge("replan", "master_itinerary")
    graph.add_edge("finalize", END)
    return graph.compile()


_app = build_graph()


def _validate_request(start_date: str, end_date: str, travelers: int, budget_inr: float) -> None:
    try:
        trip_days = (date.fromisoformat(end_date) - date.fromisoformat(start_date)).days + 1
    except ValueError as exc:
        raise ValueError("Dates must use YYYY-MM-DD format.") from exc
    if trip_days not in (1, 2, 3):
        raise ValueError("WeekendWise supports trips of 1 to 3 days.")
    if travelers < 1:
        raise ValueError("Travelers must be at least 1.")
    if budget_inr <= 0:
        raise ValueError("Budget must be greater than zero.")


def plan_weekend(
    destination: str,
    start_date: str,
    end_date: str,
    travelers: int = 2,
    budget_inr: float = 10000,
    transport_preference: str = "Local taxi",
    interests: Optional[list[str]] = None,
    demo_mode: Optional[bool] = None,
    max_replans: Optional[int] = None,
) -> WeekendState:
    """Plan a 1-3 day weekend with bounded validation-driven replanning."""
    _validate_request(start_date, end_date, travelers, budget_inr)
    initial: WeekendState = {
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "travelers": travelers,
        "budget_inr": float(budget_inr),
        "transport_preference": transport_preference,
        "interests": interests or [],
        "demo_mode": DEMO_MODE if demo_mode is None else demo_mode,
        "max_replans": MAX_REPLANS if max_replans is None else max_replans,
        "replan_count": 0,
        "replan_issues": [],
        "weather": [],
        "events": [],
        "activities": [],
        "restaurants": [],
        "route": {},
        "itinerary": [],
        "budget_breakdown": {},
        "validation": {"status": "FAIL", "issues": [], "recommendations": []},
        "validation_history": [],
        "execution_trace": [],
        "errors": [],
        "final_plan": None,
    }
    return _app.invoke(initial)


plan_trip = plan_weekend
