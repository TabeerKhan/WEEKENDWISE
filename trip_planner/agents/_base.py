"""Small shared helpers for WeekendWise agents."""

from __future__ import annotations

from datetime import date
from rich.console import Console

console = Console()


def days(state: dict) -> int:
    try:
        return (date.fromisoformat(state["end_date"]) - date.fromisoformat(state["start_date"])).days + 1
    except (KeyError, ValueError):
        return 0


def event(agent: str, status: str, message: str, state: dict) -> dict:
    return {"execution_trace": [{
        "agent": agent,
        "status": status,
        "message": message,
        "attempt": state.get("replan_count", 0),
    }]}
