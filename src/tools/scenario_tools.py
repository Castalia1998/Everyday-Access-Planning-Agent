"""Scenario simulation tools for station-area interventions."""

from __future__ import annotations

import pandas as pd

from src.tools.spatial_tools import calculate_planning_priority

INTERVENTION_MAP = {
    "improve_crossing_safety": ("crossing_safety", 0.15),
    "increase_shade": ("shade_quality", 0.15),
    "improve_barrier_free_access": ("barrier_free_access", 0.15),
    "improve_hawker_access": ("hawker_access", 0.15),
}


def simulate_intervention(
    df: pd.DataFrame, intervention_type: str, target_areas: list[str]
) -> pd.DataFrame:
    """Simulate an intervention by improving one relevant indicator and recalculating scores."""
    if intervention_type not in INTERVENTION_MAP:
        raise ValueError(f"Unknown intervention_type: {intervention_type}")
    indicator, delta = INTERVENTION_MAP[intervention_type]
    if indicator not in df.columns:
        raise ValueError(f"Missing intervention indicator: {indicator}")

    out = df.copy()
    mask = out["station_area"].isin(target_areas)
    out.loc[mask, indicator] = (out.loc[mask, indicator] + delta).clip(upper=1.0)
    out = calculate_planning_priority(out)
    out["scenario_intervention"] = intervention_type
    return out
