"""WeekendWise configuration loaded from environment variables."""

from __future__ import annotations

import os

WEEKENDWISE_NAME = "WeekendWise"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock").lower()
CURRENCY = os.getenv("CURRENCY", "INR").upper()
MAX_REPLANS = int(os.getenv("MAX_REPLANS", "3"))
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() in {"1", "true", "yes"}

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION", "2024-12-01-preview")
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY", "")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")

LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "4096"))


def money(value: float) -> str:
    return f"₹{value:,.0f}" if CURRENCY == "INR" else f"{CURRENCY} {value:,.0f}"
