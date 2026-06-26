"""Tools for summarizing synthetic citizen feedback."""

from __future__ import annotations

import pandas as pd

NEGATIVE_WEIGHT = 1.0
NEUTRAL_WEIGHT = 0.5
POSITIVE_WEIGHT = 0.1


def load_citizen_feedback(path: str) -> pd.DataFrame:
    """Load synthetic citizen feedback from CSV."""
    df = pd.read_csv(path)
    required = {"station_area", "stakeholder_group", "comment", "topic", "sentiment"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    return df


def calculate_citizen_concern_score(feedback_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate a simple concern score by station area from feedback sentiment."""
    weights = {
        "negative": NEGATIVE_WEIGHT,
        "neutral": NEUTRAL_WEIGHT,
        "positive": POSITIVE_WEIGHT,
    }
    out = feedback_df.copy()
    out["concern_weight"] = out["sentiment"].str.lower().map(weights).fillna(NEUTRAL_WEIGHT)
    grouped = out.groupby("station_area", as_index=False)["concern_weight"].mean()
    grouped = grouped.rename(columns={"concern_weight": "citizen_concern_score"})
    return grouped


def summarize_citizen_feedback(feedback_df: pd.DataFrame, station_area: str | None = None) -> dict:
    """Summarize synthetic citizen feedback overall or for one station area."""
    df = feedback_df.copy()
    if station_area is not None:
        df = df[df["station_area"] == station_area]

    if df.empty:
        return {
            "station_area": station_area,
            "n_comments": 0,
            "top_topics": [],
            "sentiment_counts": {},
            "example_comments": [],
        }

    top_topics = df["topic"].value_counts().head(5).index.tolist()
    sentiment_counts = df["sentiment"].value_counts().to_dict()
    example_comments = df["comment"].head(3).tolist()

    return {
        "station_area": station_area or "all",
        "n_comments": int(len(df)),
        "top_topics": top_topics,
        "sentiment_counts": sentiment_counts,
        "example_comments": example_comments,
    }
