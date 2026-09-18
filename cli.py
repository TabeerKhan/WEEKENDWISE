"""Command-line entrypoint for WeekendWise."""

from __future__ import annotations

import argparse
import json

from dotenv import load_dotenv

load_dotenv()

from trip_planner import plan_weekend


def main() -> int:
    parser = argparse.ArgumentParser(description="WeekendWise - Agentic AI Weekend Planner")
    parser.add_argument("--destination", default="Vizag")
    parser.add_argument("--start", default="2026-09-19")
    parser.add_argument("--end", default="2026-09-20")
    parser.add_argument("--travelers", type=int, default=4)
    parser.add_argument("--budget", type=float, default=10000)
    parser.add_argument("--transport", default="Local taxi")
    args = parser.parse_args()
    result = plan_weekend(args.destination, args.start, args.end, args.travelers, args.budget, args.transport, ["Food", "Beaches", "Events"])
    print(json.dumps(result["final_plan"], indent=2))
    print("\nAgent activity:")
    for item in result.get("execution_trace", []):
        print(f"{item.get('status', '').upper():8} {item.get('agent')}: {item.get('message')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
