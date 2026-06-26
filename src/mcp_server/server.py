"""Read-only MCP server for synthetic Everyday Access planning tools."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

if __package__ in {None, ""}:
    ROOT_FOR_IMPORT = Path(__file__).resolve().parents[2]
    if str(ROOT_FOR_IMPORT) not in sys.path:
        sys.path.insert(0, str(ROOT_FOR_IMPORT))

from mcp.server.fastmcp import FastMCP

from src.tools.policy_tools import retrieve_policy_snippets
from src.tools.scenario_tools import INTERVENTION_MAP, simulate_intervention
from src.tools.spatial_tools import calculate_planning_priority, load_station_area_indicators, rank_priority_areas

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "station_area_indicators.csv"
DOCS_DIR = ROOT / "data" / "policy_docs"
SYNTHETIC_NOTE = (
    "Synthetic demo data only. Values are illustrative and are not real Singapore measurements."
)
POLICY_NOTE = "Synthetic demo policy texts only. These are not real policy commitments or citations."

mcp = FastMCP("everyday-access-planning-agent")


def _load_scored_data():
    indicators = load_station_area_indicators(str(DATA_PATH))
    return calculate_planning_priority(indicators)


def _row_scores(row: Any) -> dict[str, Any]:
    return {
        "station_area": row["station_area"],
        "planning_priority": float(row["planning_priority"]),
        "everyday_access_deficit": float(row["everyday_access_deficit"]),
        "public_realm_deficit": float(row["public_realm_deficit"]),
        "community_need": float(row["community_need"]),
        "citizen_concern_score": float(row.get("citizen_concern_score", 0.0)),
    }


def list_station_area_priorities(top_k: int = 5) -> dict[str, Any]:
    """Return top station-area planning priorities from synthetic demo data."""
    if top_k < 1:
        return {"error": "top_k must be at least 1", "note": SYNTHETIC_NOTE}

    scored = _load_scored_data()
    ranked = rank_priority_areas(scored, top_k=top_k)
    return {
        "note": SYNTHETIC_NOTE,
        "top_k": int(top_k),
        "results": [_row_scores(row) for _, row in ranked.iterrows()],
    }


def get_station_area_explanation(station_area: str) -> dict[str, Any]:
    """Return deterministic component scores and explanation for one station area."""
    scored = _load_scored_data()
    available = scored["station_area"].tolist()
    match = scored[scored["station_area"].str.lower() == station_area.lower()]
    if match.empty:
        return {
            "error": f"Station area not found: {station_area}",
            "available_station_areas": available,
            "note": SYNTHETIC_NOTE,
        }

    row = match.iloc[0]
    scores = _row_scores(row)
    explanation = (
        f"{row['station_area']} has a synthetic planning priority score of "
        f"{row['planning_priority']:.3f}. The score combines everyday access deficit "
        f"({row['everyday_access_deficit']:.3f}), public realm deficit "
        f"({row['public_realm_deficit']:.3f}), and community need "
        f"({row['community_need']:.3f}) using transparent deterministic weights."
    )
    return {"note": SYNTHETIC_NOTE, "scores": scores, "explanation": explanation}


def search_policy_context(query: str, top_k: int = 3) -> dict[str, Any]:
    """Search synthetic policy-style documents with deterministic keyword overlap."""
    if not query.strip():
        return {"error": "query must not be empty", "note": POLICY_NOTE, "snippets": []}
    if top_k < 1:
        return {"error": "top_k must be at least 1", "note": POLICY_NOTE, "snippets": []}

    snippets = retrieve_policy_snippets(query, str(DOCS_DIR), top_k=top_k)
    return {
        "note": POLICY_NOTE,
        "query": query,
        "snippets": [
            {
                "source_file": item["document"],
                "score": int(item["score"]),
                "snippet": item["snippet"],
            }
            for item in snippets
        ],
    }


def simulate_station_area_intervention(station_area: str, intervention_type: str) -> dict[str, Any]:
    """Simulate one supported intervention for one synthetic station area."""
    if intervention_type not in INTERVENTION_MAP:
        return {
            "error": f"Unsupported intervention_type: {intervention_type}",
            "supported_intervention_types": sorted(INTERVENTION_MAP.keys()),
            "note": SYNTHETIC_NOTE,
        }

    baseline = _load_scored_data()
    available = baseline["station_area"].tolist()
    baseline_match = baseline[baseline["station_area"].str.lower() == station_area.lower()]
    if baseline_match.empty:
        return {
            "error": f"Station area not found: {station_area}",
            "available_station_areas": available,
            "note": SYNTHETIC_NOTE,
        }

    canonical_area = baseline_match.iloc[0]["station_area"]
    scenario = simulate_intervention(baseline, intervention_type, [canonical_area])
    scenario_match = scenario[scenario["station_area"] == canonical_area].iloc[0]
    baseline_row = baseline_match.iloc[0]
    baseline_priority = float(baseline_row["planning_priority"])
    scenario_priority = float(scenario_match["planning_priority"])
    delta = scenario_priority - baseline_priority
    interpretation = (
        f"The {intervention_type} scenario changes {canonical_area}'s synthetic planning priority "
        f"from {baseline_priority:.3f} to {scenario_priority:.3f}. A lower score after intervention "
        "indicates reduced modeled need under this demo scoring approach."
    )
    return {
        "note": SYNTHETIC_NOTE,
        "station_area": canonical_area,
        "intervention_type": intervention_type,
        "baseline_planning_priority": baseline_priority,
        "scenario_planning_priority": scenario_priority,
        "change": delta,
        "interpretation": interpretation,
    }


@mcp.tool(name="list_station_area_priorities")
def mcp_list_station_area_priorities(top_k: int = 5) -> dict[str, Any]:
    """List top synthetic station-area planning priorities."""
    return list_station_area_priorities(top_k=top_k)


@mcp.tool(name="get_station_area_explanation")
def mcp_get_station_area_explanation(station_area: str) -> dict[str, Any]:
    """Explain one synthetic station-area priority score."""
    return get_station_area_explanation(station_area=station_area)


@mcp.tool(name="search_policy_context")
def mcp_search_policy_context(query: str, top_k: int = 3) -> dict[str, Any]:
    """Search synthetic policy-style context snippets."""
    return search_policy_context(query=query, top_k=top_k)


@mcp.tool(name="simulate_station_area_intervention")
def mcp_simulate_station_area_intervention(station_area: str, intervention_type: str) -> dict[str, Any]:
    """Simulate a supported intervention for one synthetic station area."""
    return simulate_station_area_intervention(
        station_area=station_area,
        intervention_type=intervention_type,
    )


def main() -> None:
    """Run the local stdio MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()