from src.agent.router import route_user_question


def test_citizen_question_routes_to_citizen():
    result = route_user_question("Can you explain why my station feels unsafe for residents?")

    assert result["stakeholder_type"] == "citizen"
    assert result["brief_style"] == "accessible"
    assert "area_explanation" in result["analysis_focus"]


def test_policy_budget_question_routes_to_policy_maker():
    result = route_user_question("How should we prioritize budget investment for implementation?")

    assert result["stakeholder_type"] == "policy_maker"
    assert result["brief_style"] == "action_oriented"
    assert "priority_ranking" in result["analysis_focus"]


def test_methodology_question_routes_to_researcher():
    result = route_user_question("Compare the method assumptions and weights in the model.")

    assert result["stakeholder_type"] == "researcher"
    assert result["brief_style"] == "analytical"
    assert "method_sensitivity" in result["analysis_focus"]


def test_shade_heat_question_routes_to_increase_shade():
    result = route_user_question("What if we add trees for heat and shade near stations?")

    assert result["scenario_type"] == "increase_shade"
    assert "scenario_comparison" in result["analysis_focus"]


def test_known_station_area_is_detected():
    result = route_user_question("Why is Toa Payoh ranked highly for access improvements?")

    assert result["target_area"] == "Toa Payoh"


def test_default_routing_when_no_keywords_match():
    result = route_user_question("Hello there")

    assert result["stakeholder_type"] == "policy_maker"
    assert result["analysis_focus"] == ["priority_ranking", "policy_alignment"]
    assert result["target_area"] is None
    assert result["scenario_type"] is None