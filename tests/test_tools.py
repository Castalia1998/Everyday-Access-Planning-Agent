from pathlib import Path
import json

import pandas as pd

from src.tools.brief_tools import generate_stakeholder_brief
from src.tools.evaluation_tools import evaluate_brief
from src.tools.feedback_tools import calculate_citizen_concern_score, load_citizen_feedback, summarize_citizen_feedback
from src.tools.policy_tools import retrieve_policy_snippets
from src.tools.scenario_tools import simulate_intervention
from src.tools.spatial_tools import calculate_planning_priority, load_station_area_indicators, rank_priority_areas
from src.tools.trace_tools import write_trace

ROOT = Path(__file__).resolve().parents[1]


def test_station_area_data_loads():
    df = load_station_area_indicators(str(ROOT / "data" / "station_area_indicators.csv"))
    assert not df.empty
    assert "station_area" in df.columns


def test_scores_are_calculated_and_ranked():
    df = load_station_area_indicators(str(ROOT / "data" / "station_area_indicators.csv"))
    scored = calculate_planning_priority(df)
    assert "planning_priority" in scored.columns
    ranked = rank_priority_areas(scored, top_k=3)
    assert len(ranked) == 3
    assert ranked["planning_priority"].is_monotonic_decreasing


def test_feedback_summary_and_concern_score():
    feedback = load_citizen_feedback(str(ROOT / "data" / "citizen_feedback.csv"))
    summary = summarize_citizen_feedback(feedback)
    assert summary["n_comments"] > 0
    concern = calculate_citizen_concern_score(feedback)
    assert "citizen_concern_score" in concern.columns


def test_policy_snippets_retrieved():
    snippets = retrieve_policy_snippets(
        "walking shade ageing access public space",
        str(ROOT / "data" / "policy_docs"),
        top_k=3,
    )
    assert len(snippets) > 0
    assert "snippet" in snippets[0]


def test_intervention_changes_scores_for_targeted_areas():
    df = load_station_area_indicators(str(ROOT / "data" / "station_area_indicators.csv"))
    baseline = calculate_planning_priority(df)
    target = [baseline.sort_values("planning_priority", ascending=False).iloc[0]["station_area"]]
    scenario = simulate_intervention(baseline, "increase_shade", target)
    before = baseline.loc[baseline["station_area"] == target[0], "planning_priority"].iloc[0]
    after = scenario.loc[scenario["station_area"] == target[0], "planning_priority"].iloc[0]
    assert after < before


def test_stakeholder_brief_modes_differ_and_evaluate():
    df = load_station_area_indicators(str(ROOT / "data" / "station_area_indicators.csv"))
    scored = calculate_planning_priority(df)
    citizen = generate_stakeholder_brief(scored, "citizen")
    researcher = generate_stakeholder_brief(scored, "researcher")
    assert citizen != researcher
    evaluation = evaluate_brief(citizen)
    assert "checks" in evaluation


def test_trace_json_can_be_written(tmp_path):
    trace_path = tmp_path / "trace.json"
    write_trace(str(trace_path), "test_step", {"x": 1}, {"y": 2})
    events = json.loads(trace_path.read_text(encoding="utf-8"))
    assert events[0]["step_name"] == "test_step"
