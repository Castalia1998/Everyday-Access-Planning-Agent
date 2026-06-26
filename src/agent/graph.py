"""Deterministic LangGraph workflow for the planning demo."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from langgraph.graph import END, StateGraph

from src.agent.router import route_user_question
from src.agent.state import PlanningAgentState
from src.tools.brief_tools import generate_stakeholder_brief
from src.tools.feedback_tools import (
    calculate_citizen_concern_score,
    load_citizen_feedback,
    summarize_citizen_feedback,
)
from src.tools.policy_tools import retrieve_policy_snippets
from src.tools.scenario_tools import simulate_intervention
from src.tools.spatial_tools import calculate_planning_priority, load_station_area_indicators, rank_priority_areas
from src.tools.trace_tools import write_trace
from src.tool_registry.executor import execute_tool

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "station_area_indicators.csv"
FEEDBACK_PATH = ROOT / "data" / "citizen_feedback.csv"
DOCS_DIR = ROOT / "data" / "policy_docs"
OUTPUTS_DIR = ROOT / "outputs"
TRACE_PATH = ROOT / "traces" / "langgraph_trace.json"


def _append_step(state: PlanningAgentState, step_name: str, outputs: dict[str, Any]) -> list[dict[str, Any]]:
    steps = list(state.get("trace_steps", []))
    steps.append({"step_name": step_name, "outputs": outputs})
    return steps



def routing_node(state: PlanningAgentState) -> PlanningAgentState:
    """Route the user question into deterministic workflow settings."""
    routing_result = route_user_question(state.get("user_question", ""))
    stakeholder_type = state.get("stakeholder_type") or routing_result["stakeholder_type"]
    brief_style = {
        "citizen": "accessible",
        "policy_maker": "action_oriented",
        "researcher": "analytical",
    }[stakeholder_type]
    return {
        "stakeholder_type": stakeholder_type,
        "routing_result": routing_result,
        "analysis_focus": routing_result["analysis_focus"],
        "target_area": routing_result["target_area"],
        "scenario_type": routing_result["scenario_type"],
        "brief_style": brief_style,
        "trace_steps": _append_step(
            state,
            "routing_node",
            {
                "routed_stakeholder_type": routing_result["stakeholder_type"],
                "effective_stakeholder_type": stakeholder_type,
                "analysis_focus": routing_result["analysis_focus"],
                "target_area": routing_result["target_area"],
                "scenario_type": routing_result["scenario_type"],
                "brief_style": brief_style,
            },
        ),
    }

def problem_framing_node(state: PlanningAgentState) -> PlanningAgentState:
    """Frame the planning task as a deterministic sequence of tool calls."""
    task_plan = [
        "load station-area and citizen feedback data",
        "calculate and rank planning priority",
        "retrieve policy-style snippets",
        "summarize citizen feedback",
        "simulate a simple intervention for priority areas",
        "generate and evaluate a stakeholder brief",
        "write outputs and trace",
    ]
    return {
        "task_plan": task_plan,
        "trace_steps": _append_step(state, "problem_framing_node", {"task_plan": task_plan}),
    }


def spatial_analysis_node(state: PlanningAgentState) -> PlanningAgentState:
    """Load synthetic station indicators and calculate priority rankings."""
    indicators = load_station_area_indicators(str(DATA_PATH))
    feedback = load_citizen_feedback(str(FEEDBACK_PATH))
    concern = calculate_citizen_concern_score(feedback)
    scored = calculate_planning_priority(indicators, concern)
    ranked = rank_priority_areas(scored, top_k=5)
    top_areas = ranked["station_area"].tolist()
    return {
        "station_area_data": indicators,
        "priority_table": ranked,
        "top_areas": top_areas,
        "trace_steps": _append_step(state, "spatial_analysis_node", {"top_areas": top_areas}),
    }


def policy_retrieval_node(state: PlanningAgentState) -> PlanningAgentState:
    """Retrieve deterministic policy-style snippets relevant to the question."""
    query = state.get("user_question") or "walking shade ageing access public space"
    snippets = retrieve_policy_snippets(query, str(DOCS_DIR), top_k=3)
    return {
        "policy_snippets": snippets,
        "trace_steps": _append_step(
            state,
            "policy_retrieval_node",
            {"documents": [item["document"] for item in snippets]},
        ),
    }


def feedback_summary_node(state: PlanningAgentState) -> PlanningAgentState:
    """Summarize synthetic citizen feedback for the brief."""
    feedback = load_citizen_feedback(str(FEEDBACK_PATH))
    summary = summarize_citizen_feedback(feedback)
    return {
        "feedback_summary": summary,
        "trace_steps": _append_step(
            state,
            "feedback_summary_node",
            {"n_comments": summary.get("n_comments", 0), "top_topics": summary.get("top_topics", [])},
        ),
    }


def scenario_simulation_node(state: PlanningAgentState) -> PlanningAgentState:
    """Simulate one simple public-realm intervention for the top priority areas."""
    priority_table = state["priority_table"]
    target_areas = state.get("top_areas", [])[:3]
    intervention_type = state.get("scenario_type") or "increase_shade"
    scenario = simulate_intervention(priority_table, intervention_type, target_areas)
    return {
        "scenario_result": scenario,
        "trace_steps": _append_step(
            state,
            "scenario_simulation_node",
            {"intervention": intervention_type, "target_areas": target_areas},
        ),
    }


def brief_generation_node(state: PlanningAgentState) -> PlanningAgentState:
    """Generate a deterministic stakeholder brief from workflow outputs."""
    brief = generate_stakeholder_brief(
        state["priority_table"],
        state.get("stakeholder_type", "policy_maker"),
        state.get("policy_snippets"),
        state.get("feedback_summary"),
    )
    return {
        "brief_text": brief,
        "trace_steps": _append_step(state, "brief_generation_node", {"brief_length": len(brief)}),
    }


def evaluation_node(state: PlanningAgentState) -> PlanningAgentState:
    """Evaluate the deterministic brief for grounding and limitations."""
    evaluation = execute_tool("urban_eval.evaluate_brief", brief_text=state["brief_text"])
    return {
        "evaluation_result": evaluation,
        "trace_steps": _append_step(state, "evaluation_node", evaluation),
    }


def output_node(state: PlanningAgentState) -> PlanningAgentState:
    """Write workflow outputs and a trace file."""
    OUTPUTS_DIR.mkdir(exist_ok=True)
    TRACE_PATH.parent.mkdir(exist_ok=True)

    priority_path = OUTPUTS_DIR / "langgraph_priority_station_areas.csv"
    scenario_path = OUTPUTS_DIR / "langgraph_scenario_result.csv"
    brief_path = OUTPUTS_DIR / "langgraph_policy_maker_brief.md"

    state["priority_table"].to_csv(priority_path, index=False)
    state["scenario_result"].to_csv(scenario_path, index=False)
    brief_path.write_text(state["brief_text"], encoding="utf-8")

    output_paths = {
        "priority_table": str(priority_path),
        "scenario_result": str(scenario_path),
        "brief": str(brief_path),
        "trace": str(TRACE_PATH),
    }
    trace_steps = _append_step(state, "output_node", {"output_paths": output_paths})
    write_trace(
        str(TRACE_PATH),
        "langgraph_planning_workflow",
        {
            "user_question": state.get("user_question", ""),
            "stakeholder_type": state.get("stakeholder_type", "policy_maker"),
        },
        {
            "top_areas": state.get("top_areas", []),
            "evaluation": state.get("evaluation_result", {}),
            "trace_steps": trace_steps,
            "output_paths": output_paths,
        },
    )
    return {"trace_steps": trace_steps, "output_paths": output_paths}


def build_planning_graph():
    """Build the deterministic LangGraph planning workflow."""
    graph = StateGraph(PlanningAgentState)
    graph.add_node("routing", routing_node)
    graph.add_node("problem_framing", problem_framing_node)
    graph.add_node("spatial_analysis", spatial_analysis_node)
    graph.add_node("policy_retrieval", policy_retrieval_node)
    graph.add_node("feedback_summary", feedback_summary_node)
    graph.add_node("scenario_simulation", scenario_simulation_node)
    graph.add_node("brief_generation", brief_generation_node)
    graph.add_node("evaluation", evaluation_node)
    graph.add_node("output", output_node)

    graph.set_entry_point("routing")
    graph.add_edge("routing", "problem_framing")
    graph.add_edge("problem_framing", "spatial_analysis")
    graph.add_edge("spatial_analysis", "policy_retrieval")
    graph.add_edge("policy_retrieval", "feedback_summary")
    graph.add_edge("feedback_summary", "scenario_simulation")
    graph.add_edge("scenario_simulation", "brief_generation")
    graph.add_edge("brief_generation", "evaluation")
    graph.add_edge("evaluation", "output")
    graph.add_edge("output", END)
    return graph.compile()


def run_planning_workflow(
    user_question: str,
    stakeholder_type: str | None = None,
) -> PlanningAgentState:
    """Run the deterministic planning workflow and return the final state."""
    app = build_planning_graph()
    initial_state: PlanningAgentState = {
        "user_question": user_question,
        "trace_steps": [],
    }
    if stakeholder_type is not None:
        initial_state["stakeholder_type"] = stakeholder_type
    return app.invoke(initial_state)