"""Deterministic spatial analysis tools for station-area planning."""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

ACCESS_COLUMNS = [
    "transit_access",
    "hawker_access",
    "grocery_access",
    "clinic_access",
    "park_access",
    "community_center_access",
]

PUBLIC_REALM_COLUMNS = [
    "sidewalk_quality",
    "crossing_safety",
    "shade_quality",
    "seating_availability",
    "street_greenery",
    "barrier_free_access",
]

COMMUNITY_NEED_COLUMNS = [
    "elderly_share",
    "children_share",
    "low_income_share",
    "rental_housing_share",
    "population_density",
]


def _ensure_columns(df: pd.DataFrame, required: list[str]) -> None:
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def load_station_area_indicators(path: str) -> pd.DataFrame:
    """Load synthetic station-area indicators from CSV."""
    df = pd.read_csv(path)
    _ensure_columns(df, ["station_area", *ACCESS_COLUMNS, *PUBLIC_REALM_COLUMNS, *COMMUNITY_NEED_COLUMNS])
    return df


def calculate_everyday_access_deficit(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate everyday access deficit from access indicators."""
    _ensure_columns(df, ACCESS_COLUMNS)
    out = df.copy()
    out["everyday_access_deficit"] = 1 - out[ACCESS_COLUMNS].mean(axis=1)
    return out


def calculate_public_realm_deficit(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate public realm deficit from street/public-space indicators."""
    _ensure_columns(df, PUBLIC_REALM_COLUMNS)
    out = df.copy()
    out["public_realm_deficit"] = 1 - out[PUBLIC_REALM_COLUMNS].mean(axis=1)
    return out


def calculate_community_need(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate normalized community need score from demographic and density indicators."""
    _ensure_columns(df, COMMUNITY_NEED_COLUMNS)
    out = df.copy()
    raw = (
        0.25 * out["elderly_share"]
        + 0.20 * out["children_share"]
        + 0.25 * out["low_income_share"]
        + 0.15 * out["rental_housing_share"]
        + 0.15 * out["population_density"]
    )
    min_val = raw.min()
    max_val = raw.max()
    if np.isclose(max_val, min_val):
        out["community_need"] = 0.0
    else:
        out["community_need"] = (raw - min_val) / (max_val - min_val)
    return out


def calculate_planning_priority(
    df: pd.DataFrame, citizen_concern_df: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """Calculate overall planning priority score.

    If citizen_concern_df is provided, it should include station_area and citizen_concern_score.
    """
    out = calculate_everyday_access_deficit(df)
    out = calculate_public_realm_deficit(out)
    out = calculate_community_need(out)

    if citizen_concern_df is not None and not citizen_concern_df.empty:
        _ensure_columns(citizen_concern_df, ["station_area", "citizen_concern_score"])
        out = out.merge(
            citizen_concern_df[["station_area", "citizen_concern_score"]],
            on="station_area",
            how="left",
        )
        out["citizen_concern_score"] = out["citizen_concern_score"].fillna(0.0)
    else:
        out["citizen_concern_score"] = 0.0

    out["planning_priority"] = (
        0.35 * out["everyday_access_deficit"]
        + 0.30 * out["public_realm_deficit"]
        + 0.25 * out["community_need"]
        + 0.10 * out["citizen_concern_score"]
    )
    return out


def rank_priority_areas(df: pd.DataFrame, top_k: int = 5) -> pd.DataFrame:
    """Return top-k station areas by planning priority."""
    if "planning_priority" not in df.columns:
        df = calculate_planning_priority(df)
    return df.sort_values("planning_priority", ascending=False).head(top_k).reset_index(drop=True)
