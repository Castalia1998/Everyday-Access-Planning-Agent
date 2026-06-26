import pytest

from src.tool_registry.executor import execute_tool, get_tool_spec, list_tools


def test_list_tools_returns_registered_tools():
    tools = list_tools()
    names = {tool.name for tool in tools}

    assert len(tools) == 12
    assert "urban_eval.evaluate_brief" in names
    assert "urban_trace.write_trace" in names


def test_get_tool_spec_returns_metadata():
    spec = get_tool_spec("urban_eval.evaluate_brief")

    assert spec.category == "urban_eval"
    assert spec.read_only is True
    assert spec.risk_level == "low"


def test_execute_tool_calls_existing_tool():
    result = execute_tool(
        "urban_eval.evaluate_brief",
        brief_text="This planning brief reports a score, mentions citizens, and includes limitations for synthetic data.",
    )

    assert result["passed"] is True
    assert result["score"] == 1.0


def test_unknown_tool_raises_clear_error():
    with pytest.raises(ValueError, match="Unknown tool"):
        get_tool_spec("urban_missing.nope")

    with pytest.raises(ValueError, match="Unknown tool"):
        execute_tool("urban_missing.nope")