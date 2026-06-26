from src.mcp_server.server import (
    get_station_area_explanation,
    list_station_area_priorities,
    search_policy_context,
    simulate_station_area_intervention,
)


def test_list_station_area_priorities_returns_top_results():
    result = list_station_area_priorities(top_k=3)

    assert "Synthetic demo data" in result["note"]
    assert result["top_k"] == 3
    assert len(result["results"]) == 3
    assert "planning_priority" in result["results"][0]


def test_get_station_area_explanation_known_area():
    result = get_station_area_explanation("Toa Payoh")

    assert result["scores"]["station_area"] == "Toa Payoh"
    assert "explanation" in result
    assert "synthetic" in result["explanation"].lower()


def test_search_policy_context_returns_snippets():
    result = search_policy_context("walking shade public space", top_k=2)

    assert result["query"] == "walking shade public space"
    assert len(result["snippets"]) > 0
    assert "source_file" in result["snippets"][0]


def test_simulate_station_area_intervention_returns_baseline_and_scenario():
    result = simulate_station_area_intervention("Toa Payoh", "increase_shade")

    assert result["station_area"] == "Toa Payoh"
    assert "baseline_planning_priority" in result
    assert "scenario_planning_priority" in result
    assert result["scenario_planning_priority"] < result["baseline_planning_priority"]