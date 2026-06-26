"""Shared state for the deterministic planning workflow."""

from __future__ import annotations

from typing import Any, TypedDict


class PlanningAgentState(TypedDict, total=False):
    """State passed between deterministic planning workflow nodes."""

    user_question: str
    stakeholder_type: str
    routing_result: dict[str, Any]
    analysis_focus: list[str]
    target_area: str | None
    scenario_type: str | None
    brief_style: str
    task_plan: list[str]
    station_area_data: Any
    priority_table: Any
    top_areas: list[str]
    policy_snippets: list[dict[str, Any]]
    feedback_summary: dict[str, Any]
    scenario_result: Any
    brief_text: str
    evaluation_result: dict[str, Any]
    trace_steps: list[dict[str, Any]]
    output_paths: dict[str, str]