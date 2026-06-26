"""Run a deterministic end-to-end demo."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.tools.brief_tools import generate_stakeholder_brief
from src.tools.evaluation_tools import evaluate_brief
from src.tools.feedback_tools import (
    calculate_citizen_concern_score,
    load_citizen_feedback,
    summarize_citizen_feedback,
)
from src.tools.policy_tools import retrieve_policy_snippets
from src.tools.spatial_tools import calculate_planning_priority, load_station_area_indicators, rank_priority_areas
from src.tools.trace_tools import write_trace

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    data_path = ROOT / "data" / "station_area_indicators.csv"
    feedback_path = ROOT / "data" / "citizen_feedback.csv"
    docs_dir = ROOT / "data" / "policy_docs"
    outputs_dir = ROOT / "outputs"
    trace_path = ROOT / "traces" / "demo_trace.json"
    outputs_dir.mkdir(exist_ok=True)

    indicators = load_station_area_indicators(str(data_path))
    feedback = load_citizen_feedback(str(feedback_path))
    concern = calculate_citizen_concern_score(feedback)
    scored = calculate_planning_priority(indicators, concern)
    ranked = rank_priority_areas(scored, top_k=5)
    policy_snippets = retrieve_policy_snippets("walking shade ageing access public space", str(docs_dir), top_k=3)
    feedback_summary = summarize_citizen_feedback(feedback)
    brief = generate_stakeholder_brief(ranked, "policy_maker", policy_snippets, feedback_summary)
    evaluation = evaluate_brief(brief)

    ranked.to_csv(outputs_dir / "priority_station_areas.csv", index=False)
    (outputs_dir / "policy_maker_brief.md").write_text(brief, encoding="utf-8")

    write_trace(
        str(trace_path),
        "deterministic_demo_run",
        {"query": "prioritize MRT station areas for everyday access improvements"},
        {"top_areas": ranked["station_area"].tolist(), "evaluation": evaluation},
    )

    print(brief)
    print(evaluation)


if __name__ == "__main__":
    main()
