"""Run the deterministic LangGraph planning workflow demo."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agent.graph import run_planning_workflow


if __name__ == "__main__":
    state = run_planning_workflow(
        "Which MRT station areas should be prioritized for everyday access and public realm improvements?",
        stakeholder_type="policy_maker",
    )
    print(state["brief_text"])
    print(state["evaluation_result"])
    print(state["output_paths"])