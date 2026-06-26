"""Deterministic stakeholder brief templates."""

from __future__ import annotations

import pandas as pd


def _top_area_sentence(row: pd.Series) -> str:
    return (
        f"{row['station_area']} has a planning priority score of "
        f"{row['planning_priority']:.3f}, with access deficit "
        f"{row['everyday_access_deficit']:.3f}, public realm deficit "
        f"{row['public_realm_deficit']:.3f}, and community need "
        f"{row['community_need']:.3f}."
    )


def generate_stakeholder_brief(
    analysis_result: pd.DataFrame,
    stakeholder_type: str,
    policy_snippets: list[dict] | None = None,
    feedback_summary: dict | None = None,
) -> str:
    """Generate a deterministic brief for citizen, policy-maker, or researcher audiences."""
    if stakeholder_type not in {"citizen", "policy_maker", "researcher"}:
        raise ValueError("stakeholder_type must be citizen, policy_maker, or researcher")

    ranked = analysis_result.sort_values("planning_priority", ascending=False).head(3)
    top_lines = "\n".join(f"- {_top_area_sentence(row)}" for _, row in ranked.iterrows())
    policy_line = ""
    if policy_snippets:
        docs = ", ".join(item["document"] for item in policy_snippets[:3])
        policy_line = f"\nRelevant policy-style documents retrieved: {docs}."

    feedback_line = ""
    if feedback_summary:
        feedback_line = (
            f"\nCitizen feedback summary: {feedback_summary.get('n_comments', 0)} comments; "
            f"top topics include {', '.join(feedback_summary.get('top_topics', []))}."
        )

    limitation = (
        "\nLimitations: This demo uses synthetic data and transparent scoring rules. "
        "The outputs should be interpreted as workflow demonstration results, not as real planning evidence."
    )

    if stakeholder_type == "citizen":
        intro = (
            "This brief explains, in plain language, which MRT station areas may need "
            "more attention for everyday access and public-realm improvements."
        )
        recommendation = (
            "\nSuggested focus: improve comfort and safety on everyday walking routes, "
            "especially shade, crossings, seating, and barrier-free access."
        )
    elif stakeholder_type == "policy_maker":
        intro = (
            "This brief identifies priority station areas for targeted public-realm and "
            "everyday-access interventions under resource constraints."
        )
        recommendation = (
            "\nSuggested focus: prioritize interventions where access deficits, public-realm "
            "deficits, community need, and citizen concerns overlap. Track before/after indicators."
        )
    else:
        intro = (
            "This brief summarizes a transparent scoring workflow for station-area planning "
            "prioritization, intended for methodological inspection and extension."
        )
        recommendation = (
            "\nSuggested focus: test sensitivity to weighting choices, replace synthetic indicators "
            "with measured data, and validate rankings against expert review."
        )

    return f"{intro}\n\nTop priority station areas:\n{top_lines}{policy_line}{feedback_line}{recommendation}{limitation}\n"
