"""Executor for registered deterministic planning tools."""

from __future__ import annotations

from typing import Any, Callable

from src.tool_registry.registry import TOOL_SPECS
from src.tool_registry.schemas import ToolSpec
from src.tools.brief_tools import generate_stakeholder_brief
from src.tools.evaluation_tools import evaluate_brief
from src.tools.feedback_tools import summarize_citizen_feedback
from src.tools.policy_tools import retrieve_policy_snippets
from src.tools.scenario_tools import simulate_intervention
from src.tools.spatial_tools import (
    calculate_community_need,
    calculate_everyday_access_deficit,
    calculate_planning_priority,
    calculate_public_realm_deficit,
    load_station_area_indicators,
    rank_priority_areas,
)
from src.tools.trace_tools import write_trace

_TOOL_FUNCTIONS: dict[str, Callable[..., Any]] = {
    "urban_data.load_station_area_indicators": load_station_area_indicators,
    "urban_analysis.calculate_everyday_access_deficit": calculate_everyday_access_deficit,
    "urban_analysis.calculate_public_realm_deficit": calculate_public_realm_deficit,
    "urban_analysis.calculate_community_need": calculate_community_need,
    "urban_analysis.calculate_planning_priority": calculate_planning_priority,
    "urban_analysis.rank_priority_areas": rank_priority_areas,
    "urban_policy.retrieve_policy_snippets": retrieve_policy_snippets,
    "urban_feedback.summarize_citizen_feedback": summarize_citizen_feedback,
    "urban_scenario.simulate_intervention": simulate_intervention,
    "urban_brief.generate_stakeholder_brief": generate_stakeholder_brief,
    "urban_eval.evaluate_brief": evaluate_brief,
    "urban_trace.write_trace": write_trace,
}


def list_tools() -> list[ToolSpec]:
    """Return all registered deterministic tool specs."""
    return list(TOOL_SPECS.values())


def get_tool_spec(tool_name: str) -> ToolSpec:
    """Return metadata for one registered tool, or raise a clear error."""
    try:
        return TOOL_SPECS[tool_name]
    except KeyError as exc:
        raise ValueError(f"Unknown tool: {tool_name}") from exc


def execute_tool(tool_name: str, **kwargs: Any) -> Any:
    """Execute a registered deterministic tool by name."""
    get_tool_spec(tool_name)
    function = _TOOL_FUNCTIONS[tool_name]
    return function(**kwargs)