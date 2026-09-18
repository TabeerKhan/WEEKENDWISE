"""WeekendWise Panel dashboard.

Run with: python -m panel serve dashboard.py --show
"""

from __future__ import annotations

import html
import threading
from datetime import date, timedelta

import panel as pn
from dotenv import load_dotenv

load_dotenv()

from trip_planner.config import money
from trip_planner.graph import plan_weekend

pn.extension(sizing_mode="stretch_width")

INTERESTS = ["Food", "Beaches", "Nature", "Adventure", "Events", "Shopping", "History", "Nightlife", "Photography", "Relaxation"]

CSS = """
:root { --ink:#14223b; --blue:#248dd8; --blue-dark:#1973b8; --sky:#eef5fc; --line:#d9e6f2; --coral:#ef765f; }
body { background:#eef5fc; color:var(--ink); font-family:'Segoe UI',Arial,sans-serif; }
.ww-shell { width:100%; min-height:100vh; padding:0; background:radial-gradient(circle at 74% 14%,#ffffff 0,#eef5fc 38%,#e5f1fb 100%); }
.ww-frame { min-height:100vh; }
.ww-sidebar { background:#ffffff; border-right:1px solid #dce8f3; padding:24px 20px 30px; min-height:100vh; box-shadow:3px 0 14px #1a79b50d; }
.ww-workspace { padding:34px 42px 70px; max-width:1180px; }
.brand { display:flex; align-items:center; gap:12px; margin-bottom:22px; }
.brand-icon { width:48px; height:48px; display:grid; place-items:center; border-radius:14px; background:linear-gradient(145deg,#dff3ff,#b9e2fa); color:#1973b8; font-size:24px; box-shadow:0 5px 14px #248dd82e; }
.brand-name { color:#192944; font:800 22px 'Segoe UI',Arial,sans-serif; }
.brand-tag { color:#7890a6; font:12px 'Segoe UI',Arial,sans-serif; }
.eyebrow { color:var(--coral); letter-spacing:2px; text-transform:uppercase; font:700 11px Arial,sans-serif; }
.title { font-size:36px; line-height:1; color:#182740; margin:8px 0 10px; letter-spacing:-1px; }
.subtitle { color:#657d95; font:15px 'Segoe UI',Arial,sans-serif; margin-bottom:26px; }
.panel { background:#ffffffde; border:1px solid var(--line); border-radius:14px; padding:22px; box-shadow:0 10px 28px #237bb512; }
.section-title { color:#203b61; font:700 17px 'Segoe UI',Arial,sans-serif; margin:0 0 14px; }
.agent { display:grid; grid-template-columns:180px 1fr auto; align-items:center; gap:12px; padding:12px 10px; margin:4px -10px; border-bottom:1px solid #edf2ef; font:14px Arial,sans-serif; border-radius:8px; }
.agent:last-child { border-bottom:0; }
.agent-status { margin-left:auto; color:#4d7771; font-size:12px; }
.agent:nth-child(odd) { background:#f5fbf8; }
.day { border-left:6px solid var(--coral); padding:16px 18px; margin:14px 0; background:linear-gradient(110deg,#fffdf9,#fff4ea); border-radius:0 12px 12px 0; }
.day:nth-child(even) { border-left-color:#f3b544; background:linear-gradient(110deg,#fffdf9,#fffbea); }
.day-head { color:#1973b8; font:700 17px Arial,sans-serif; letter-spacing:.4px; }
.item { padding:12px 10px; border-bottom:1px solid #edf2ef; font:14px Arial,sans-serif; border-radius:8px; }
.item:last-child { border-bottom:0; }
.item:hover { background:#ffffffcc; }
.meta { color:#60777b; font-size:12px; margin-top:4px; }
.metric { background:linear-gradient(145deg,#e9f8f1,#eaf3ff); border:1px solid #d7ebe3; border-radius:10px; padding:14px; font:14px Arial,sans-serif; }
.warning { color:#a75232; background:#fff1e9; padding:10px; border-radius:5px; font:13px Arial,sans-serif; }
.pass { color:#17654e; background:#e8f7ee; padding:10px; border-radius:5px; font:13px Arial,sans-serif; }
.form-panel { background:#fffdf8; border-top:5px solid var(--coral); }
.field-label { color:#527078; font:700 11px Arial,sans-serif; text-transform:uppercase; letter-spacing:1px; }
.cta button { background:var(--coral)!important; border:0!important; border-radius:9px!important; font-weight:700!important; box-shadow:0 8px 16px #ef765f45!important; }
.source-pill { display:inline-block; background:#e6f5ee; color:#17654e; border-radius:999px; padding:5px 10px; font:700 11px Arial,sans-serif; }
.kpi-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:10px; margin-bottom:14px; }
.kpi { background:linear-gradient(145deg,#fff4e8,#e9f8f1); border-left:4px solid var(--coral); border-radius:10px; padding:14px; font:13px Arial,sans-serif; box-shadow:0 5px 14px #154b5010; }
.kpi:nth-child(2) { border-left-color:#f3b544; }
.kpi:nth-child(3) { border-left-color:#5a9ee8; }
.kpi:nth-child(4) { border-left-color:#49a879; }
.route-line { color:#1973b8; font:700 15px Arial,sans-serif; background:#edf6ff; padding:15px; border-radius:10px; }
.source-live { background:#e4f2ff; color:#1d5b92; }
.source-demo { background:#fff1d8; color:#965c13; }
@media (max-width: 720px) { .title { font-size:32px; } .ww-workspace { padding:24px 16px 40px; } .ww-sidebar { min-height:auto; border-right:0; } .agent { grid-template-columns:1fr; gap:4px; } .agent-status { margin-left:0; } }
"""


def esc(value: object) -> str:
    return html.escape(str(value))


def agent_html(trace: list[dict]) -> str:
    if not trace:
        return '<div class="meta">Agent execution will appear here after planning.</div>'
    rows = []
    for item in trace:
        status = item.get("status", "complete")
        icon = {"complete": "✓", "warning": "⚠", "failed": "!", "running": "…"}.get(status, "•")
        rows.append(f'<div class="agent"><b>{icon} {esc(item.get("agent", "Agent"))}</b><span>{esc(item.get("message", ""))}</span><span class="agent-status">attempt {item.get("attempt", 0)}</span></div>')
    return "".join(rows)


def result_html(result: dict) -> str:
    plan = result.get("final_plan") or {}
    validation = plan.get("validation", {})
    budget = plan.get("budget", {})
    route = plan.get("route", {})
    weather = plan.get("weather", [])
    days = plan.get("days", [])
    day_groups: dict[str, list] = {}
    for item in days:
        day_groups.setdefault(item.get("date", ""), []).append(item)
    day_html = ""
    for day, items in day_groups.items():
        cards = "".join(
            f'<div class="item"><b>{esc(item.get("time"))} · {esc(item.get("title"))}</b>'
            f'<div>{esc(item.get("location"))} · {item.get("duration_minutes", 0)} min · {money(item.get("cost_inr", 0))}</div>'
            f'<div class="meta">Travel {item.get("travel_minutes", 0)} min · {esc(item.get("reason"))}</div></div>'
            for item in items
        )
        day_html += f'<div class="day"><div class="day-head">{esc(day)}</div>{cards}</div>'
    weather_html = "".join(f'<div class="metric"><b>{esc(w.get("date"))}</b><br>{esc(w.get("condition"))}, {w.get("temperature_c")} C<br><span class="meta">Rain {w.get("rain_chance", 0)}% · Outdoor score {w.get("outdoor_score", 0)}/100</span></div>' for w in weather)
    issue_html = "".join(f'<li>{esc(issue)}</li>' for issue in validation.get("issues", [])) or "<li>All constraints passed.</li>"
    status_class = "pass" if validation.get("status") == "PASS" else "warning"
    budget_rows = "".join(f'<div class="item"><b>{esc(key)}</b><span style="float:right">{money(value)}</span></div>' for key, value in budget.items() if key not in {"budget", "remaining"})
    source_class = "source-demo" if plan.get("demo_mode") else "source-live"
    source_label = "Demo Mode sample data" if plan.get("demo_mode") else "Live API data"
    return f'''<div class="kpi-grid"><div class="kpi"><b>{esc(plan.get("destination"))}</b><br>Destination</div><div class="kpi"><b>{plan.get("replans", 0)}</b><br>Replans</div><div class="kpi"><b>{money(budget.get("total", 0))}</b><br>Estimated total</div><div class="kpi"><b>{esc(validation.get("status", "FAIL"))}</b><br>Validation</div></div><div class="panel"><div class="section-title">Final Weekend Itinerary · {esc(plan.get("destination"))}</div><span class="source-pill {source_class}">{source_label}</span>{day_html}</div>
    <div style="height:16px"></div><div class="panel"><div class="section-title">Budget Dashboard</div>{budget_rows}<div class="item"><b>Total</b><span style="float:right">{money(budget.get("total", 0))}</span></div><div class="item"><b>Budget</b><span style="float:right">{money(budget.get("budget", 0))}</span></div><div class="item"><b>Remaining</b><span style="float:right">{money(budget.get("remaining", 0))}</span></div></div>
    <div style="height:16px"></div><div class="panel"><div class="section-title">Weather</div><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px">{weather_html}</div><p class="meta">Outdoor activities were scheduled in the higher-score windows; the weather source is labelled Demo Mode when live data is unavailable.</p></div>
    <div style="height:16px"></div><div class="panel"><div class="section-title">Route</div><p class="route-line">{" ↓ ".join(esc(stop) for stop in route.get("stops", []))}</p><div class="meta">{route.get("total_distance_km", 0)} km · {route.get("total_travel_minutes", 0)} min · {esc(route.get("transport_method", ""))} · {money(route.get("transport_cost_inr", 0))}</div></div>
    <div style="height:16px"></div><div class="panel"><div class="section-title">Validator</div><div class="{status_class}"><b>{esc(validation.get("status", "FAIL"))}</b><ul>{issue_html}</ul></div><p class="meta">Replans: {plan.get("replans", 0)} · {"Demo Mode" if plan.get("demo_mode") else "Live integrations"}</p></div>'''


class WeekendWiseDashboard(pn.viewable.Viewer):
    def __init__(self, **params):
        super().__init__(**params)
        today = date.today()
        self.destination = pn.widgets.TextInput(name="Destination", placeholder="e.g. Vizag")
        self.start = pn.widgets.DatePicker(name="Start date", value=today + timedelta(days=1))
        self.end = pn.widgets.DatePicker(name="End date", value=today + timedelta(days=2))
        self.travelers = pn.widgets.IntInput(name="Travelers", value=2, start=1, end=20)
        self.budget = pn.widgets.IntInput(name="Total budget (INR)", value=10000, start=1)
        self.transport = pn.widgets.Select(name="Transportation", options=["Local taxi", "Public transport", "Walking + taxi", "Rental vehicle"], value="Local taxi")
        self.interests = pn.widgets.CheckBoxGroup(name="Interests", options=INTERESTS, value=["Food", "Beaches", "Events"])
        self.button = pn.widgets.Button(name="Plan My Weekend", button_type="primary", height=48, css_classes=["cta"])
        self.button.on_click(self._plan)
        self.status = pn.pane.HTML('<div class="panel"><div class="section-title">Agent Activity</div><div class="meta">Enter your weekend requirements and start planning.</div><div class="agent-grid"><div class="agent"><b>🤖 Master Planner</b><span>Requirements understood</span><span class="agent-status">ready</span></div><div class="agent"><b>🌦 Weather Agent</b><span>Weather check</span><span class="agent-status">ready</span></div><div class="agent"><b>🗺 Route Agent</b><span>Route optimization</span><span class="agent-status">ready</span></div></div></div>')
        self.result = pn.pane.HTML("", sizing_mode="stretch_width")

    def _plan(self, _):
        self.button.disabled = True
        self.status.object = '<div class="panel"><div class="section-title">Agent Activity</div><div class="meta">Running WeekendWise agents...</div></div>'
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            result = plan_weekend(self.destination.value, self.start.value.isoformat(), self.end.value.isoformat(), self.travelers.value, self.budget.value, self.transport.value, list(self.interests.value), True)
            self.status.object = f'<div class="panel"><div class="section-title">Agent Activity</div>{agent_html(result.get("execution_trace", []))}</div>'
            self.result.object = result_html(result)
        except Exception as exc:
            self.status.object = f'<div class="panel warning">{esc(exc)}</div>'
        finally:
            self.button.disabled = False

    def __panel__(self):
        form = pn.Column(pn.pane.HTML('<div class="brand"><div class="brand-icon">✦</div><div><div class="brand-name">WeekendWise</div><div class="brand-tag">AI-powered weekend planner</div></div></div><hr>'), pn.pane.HTML('<div class="section-title">Plan your escape</div>'), self.destination, pn.Row(self.start, self.end), pn.Row(self.travelers, self.budget), self.transport, self.interests, self.button, css_classes=["ww-sidebar"], width=320)
        content = pn.Column(pn.pane.HTML('<div class="eyebrow">AGENTIC AI WEEKEND PLANNER</div><div class="title">Plan your weekend.</div><div class="subtitle">A short, thoughtful itinerary shaped around your time, budget, and interests.</div><span class="source-pill">Demo Mode ready · live weather optional</span>'), pn.Spacer(height=24), self.status, self.result, sizing_mode="stretch_width", css_classes=["ww-workspace"])
        return pn.Row(form, content, sizing_mode="stretch_width", css_classes=["ww-frame"], stylesheets=[CSS])


app = WeekendWiseDashboard()
pn.panel(app).servable(title="WeekendWise")
