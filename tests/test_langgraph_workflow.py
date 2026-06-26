from pathlib import Path

from src.agent.graph import run_planning_workflow

ROOT = Path(__file__).resolve().parents[1]


def test_langgraph_workflow_returns_state_and_outputs():
    state = run_planning_workflow(
        "Which MRT station areas should be prioritized for everyday access and public realm improvements?",
        stakeholder_type="policy_maker",
    )

    assert isinstance(state, dict)
    assert "priority_table" in state
    assert not state["priority_table"].empty
    assert state.get("brief_text")
    assert "evaluation_result" in state
    assert "routing_result" in state
    assert (ROOT / "traces" / "langgraph_trace.json").exists()


def test_langgraph_workflow_can_infer_stakeholder_type():
    state = run_planning_workflow("Can you explain why my station needs better shade?")

    assert state["stakeholder_type"] == "citizen"
    assert state["brief_style"] == "accessible"
    assert state["scenario_type"] == "increase_shade"