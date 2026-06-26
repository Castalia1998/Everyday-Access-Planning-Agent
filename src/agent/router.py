"""Deterministic routing for natural-language planning questions."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
STATION_DATA_PATH = ROOT / "data" / "station_area_indicators.csv"

CITIZEN_KEYWORDS = ["resident", "citizen", "my area", "my station", "explain", "why is"]
POLICY_MAKER_KEYWORDS = ["policy", "budget", "prioritize", "investment", "intervention", "implementation"]
RESEARCHER_KEYWORDS = ["method", "sensitivity", "weights", "compare", "assumptions", "model"]

FOCUS_KEYWORDS = {
    "priority_ranking": ["prioritize", "rank", "which areas"],
    "area_explanation": ["why", "explain", "my area", "my station"],
    "scenario_comparison": ["scenario", "intervention", "improve", "what if"],
    "method_sensitivity": ["sensitivity", "weights", "method", "assumptions"],
    "citizen_feedback": ["feedback", "concerns", "resident", "citizen"],
    "policy_alignment": ["policy", "strategy", "planning goal"],
}

SCENARIO_KEYWORDS = [
    ("increase_shade", ["shade", "hot", "heat", "trees"]),
    ("improve_crossing_safety", ["crossing", "safety", "road"]),
    ("improve_barrier_free_access", ["elderly", "wheelchair", "accessible", "barrier-free"]),
    ("improve_hawker_access", ["hawker", "food", "daily services"]),
]

BRIEF_STYLE_BY_STAKEHOLDER = {
    "citizen": "accessible",
    "policy_maker": "action_oriented",
    "researcher": "analytical",
}


def _contains_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def _detect_station_area(user_question: str) -> str | None:
    question = user_question.lower()
    station_df = pd.read_csv(STATION_DATA_PATH, usecols=["station_area"])
    for station_area in station_df["station_area"]:
        if str(station_area).lower() in question:
            return str(station_area)
    return None


def route_user_question(user_question: str) -> dict:
    """Route a user question into deterministic workflow settings."""
    question = user_question.lower()

    if _contains_any(question, CITIZEN_KEYWORDS):
        stakeholder_type = "citizen"
    elif _contains_any(question, RESEARCHER_KEYWORDS):
        stakeholder_type = "researcher"
    elif _contains_any(question, POLICY_MAKER_KEYWORDS):
        stakeholder_type = "policy_maker"
    else:
        stakeholder_type = "policy_maker"

    analysis_focus = [focus for focus, keywords in FOCUS_KEYWORDS.items() if _contains_any(question, keywords)]
    if not analysis_focus:
        analysis_focus = ["priority_ranking", "policy_alignment"]

    scenario_type = None
    for candidate, keywords in SCENARIO_KEYWORDS:
        if _contains_any(question, keywords):
            scenario_type = candidate
            break

    return {
        "stakeholder_type": stakeholder_type,
        "analysis_focus": analysis_focus,
        "target_area": _detect_station_area(user_question),
        "scenario_type": scenario_type,
        "brief_style": BRIEF_STYLE_BY_STAKEHOLDER[stakeholder_type],
    }