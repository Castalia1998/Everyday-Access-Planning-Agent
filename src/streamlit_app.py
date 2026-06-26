"""Mobile-style Streamlit interface for the Everyday Access Planning Agent."""

from __future__ import annotations

from html import escape
from pathlib import Path
import sys
from typing import Any

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agent.graph import run_planning_workflow
from src.tool_registry.executor import list_tools
from src.tools.spatial_tools import load_station_area_indicators

DATA_PATH = ROOT / "data" / "station_area_indicators.csv"
EXAMPLE_QUESTIONS = [
    "Can you explain why Toa Payoh feels hot for residents?",
    "How should policy makers prioritize budget investment for crossing safety?",
    "Compare the method assumptions and weights in the model.",
    "Which MRT station areas should be prioritized for everyday access and public realm improvements?",
]


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        html, body, [data-testid="stAppViewContainer"] {
            background: #bfc8d4;
        }
        [data-testid="stHeader"] {
            background: transparent;
        }
        .block-container {
            max-width: 430px;
            padding: 1.2rem 1rem 1.4rem;
            margin-top: 1.2rem;
            margin-bottom: 1.2rem;
            background: #f8f5ee;
            border: 3px solid #111111;
            border-radius: 34px;
            box-shadow: 0 18px 42px rgba(17, 24, 39, 0.26);
        }
        .app-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.25rem;
        }
        .brand {
            font-weight: 900;
            font-size: 1rem;
            letter-spacing: 0;
        }
        .status-pill, .tiny-pill {
            display: inline-flex;
            align-items: center;
            border: 2px solid #111111;
            border-radius: 999px;
            padding: 0.28rem 0.58rem;
            background: #ffffff;
            font-size: 0.78rem;
            font-weight: 700;
            margin: 0.16rem 0.12rem 0.16rem 0;
        }
        .hero-title {
            font-size: 2.55rem;
            line-height: 0.98;
            font-weight: 950;
            letter-spacing: 0;
            margin: 0.2rem 0 0.45rem;
        }
        .hero-prompt {
            font-size: 1.12rem;
            line-height: 1.25;
            color: #242424;
            margin-bottom: 0.9rem;
        }
        .notice {
            border: 2px solid #111111;
            border-radius: 18px;
            background: #fff3bf;
            padding: 0.75rem 0.85rem;
            font-size: 0.88rem;
            font-weight: 700;
            margin: 0.7rem 0 1rem;
        }
        .mobile-card {
            border: 2px solid #111111;
            border-radius: 22px;
            padding: 1rem;
            margin: 0.75rem 0;
            box-shadow: 0 3px 0 #111111;
        }
        .card-white { background: #fffdf7; }
        .card-lavender { background: #dcd8ff; }
        .card-yellow { background: #ffe99c; }
        .card-mint { background: #aeead8; }
        .card-brief { background: #fffaf0; }
        .card-dark {
            background: #111111;
            color: #ffffff;
            border-color: #111111;
            box-shadow: none;
        }
        .section-label {
            font-size: 0.78rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.25rem;
        }
        .card-title {
            font-size: 1.35rem;
            line-height: 1.05;
            font-weight: 950;
            margin: 0 0 0.5rem;
        }
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.45rem;
            margin: 0.8rem 0;
        }
        .metric-tile {
            border: 2px solid #111111;
            border-radius: 18px;
            background: #ffffff;
            padding: 0.65rem 0.5rem;
            min-height: 82px;
        }
        .metric-value {
            display: block;
            font-size: 1.45rem;
            line-height: 1;
            font-weight: 950;
            margin-bottom: 0.3rem;
        }
        .metric-label {
            font-size: 0.68rem;
            line-height: 1.12;
            font-weight: 800;
            color: #343434;
        }
        .example-card {
            border: 2px solid #111111;
            border-radius: 16px;
            padding: 0.62rem 0.7rem;
            background: #ffffff;
            min-height: 74px;
            font-size: 0.82rem;
            font-weight: 700;
            margin-bottom: 0.4rem;
        }
        .station-card {
            border: 2px solid #111111;
            border-radius: 18px;
            background: #ffffff;
            padding: 0.75rem;
            margin: 0.55rem 0;
        }
        .station-name {
            font-size: 1.08rem;
            font-weight: 950;
            margin-bottom: 0.25rem;
        }
        .station-score {
            font-size: 1.55rem;
            font-weight: 950;
            line-height: 1;
            float: right;
        }
        .station-detail {
            clear: both;
            font-size: 0.78rem;
            line-height: 1.25;
            color: #333333;
        }
        .bottom-nav {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0.35rem;
            background: #111111;
            color: #ffffff;
            border-radius: 24px;
            padding: 0.5rem;
            margin-top: 1rem;
            position: sticky;
            bottom: 0.75rem;
            z-index: 5;
        }
        .bottom-nav span {
            text-align: center;
            font-size: 0.76rem;
            font-weight: 900;
            padding: 0.45rem 0.1rem;
            border-radius: 999px;
        }
        .bottom-nav span:first-child {
            color: #111111;
            background: #ffffff;
        }
        div[data-testid="stForm"] {
            border: 2px solid #111111;
            border-radius: 22px;
            padding: 1rem;
            background: #fffdf7;
            box-shadow: 0 3px 0 #111111;
        }
        .stButton > button, .stFormSubmitButton > button {
            width: 100%;
            border: 2px solid #111111;
            border-radius: 999px;
            background: #111111;
            color: #ffffff;
            font-weight: 900;
        }
        div[data-baseweb="select"] > div, textarea {
            border: 2px solid #111111 !important;
            border-radius: 16px !important;
        }
        h1, h2, h3, p {
            letter-spacing: 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _html(text: Any) -> str:
    return escape(str(text))


def _metric_strip(tool_count: int, station_count: int) -> None:
    st.markdown(
        f"""
        <div class="metric-grid">
            <div class="metric-tile"><span class="metric-value">{tool_count}</span><span class="metric-label">registered tools</span></div>
            <div class="metric-tile"><span class="metric-value">{station_count}</span><span class="metric-label">station areas</span></div>
            <div class="metric-tile"><span class="metric-value">3</span><span class="metric-label">stakeholder modes</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _state_preview(state: dict[str, Any]) -> dict[str, Any]:
    preview = {}
    for key, value in state.items():
        if isinstance(value, pd.DataFrame):
            preview[key] = {"rows": int(len(value)), "columns": list(value.columns)}
        else:
            preview[key] = value
    return preview


def _registered_tools_table() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "name": spec.name,
                "category": spec.category,
                "read_only": spec.read_only,
                "risk_level": spec.risk_level,
                "description": spec.description,
            }
            for spec in list_tools()
        ]
    )


def _format_score(value: Any) -> str:
    try:
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return "n/a"


def _station_cards(priority_table: pd.DataFrame | None) -> None:
    if priority_table is None or priority_table.empty:
        st.caption("No priority table available yet.")
        return

    for _, row in priority_table.head(3).iterrows():
        st.markdown(
            f"""
            <div class="station-card">
                <div class="station-score">{_format_score(row.get("planning_priority"))}</div>
                <div class="station-name">{_html(row.get("station_area", "Unknown"))}</div>
                <div class="station-detail">
                    Access deficit: {_format_score(row.get("everyday_access_deficit"))}<br>
                    Public realm deficit: {_format_score(row.get("public_realm_deficit"))}<br>
                    Community need: {_format_score(row.get("community_need"))}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _pill_row(values: dict[str, Any]) -> None:
    pills = "".join(
        f'<span class="tiny-pill">{_html(label)}: {_html(value if value else "None")}</span>'
        for label, value in values.items()
    )
    st.markdown(pills, unsafe_allow_html=True)


def _example_buttons() -> None:
    st.markdown(
        '<div class="mobile-card card-mint"><div class="section-label">Try a prompt</div><div class="card-title">Example questions</div></div>',
        unsafe_allow_html=True,
    )
    for idx, question in enumerate(EXAMPLE_QUESTIONS):
        st.markdown(f'<div class="example-card">{_html(question)}</div>', unsafe_allow_html=True)
        if st.button("Use this question", key=f"example_{idx}"):
            st.session_state["user_question"] = question
            st.rerun()


def _render_static_shell(tool_count: int, station_count: int) -> None:
    st.markdown(
        """
        <div class="app-header">
            <div class="brand">Everyday Access</div>
            <div class="status-pill">menu</div>
        </div>
        <div class="hero-title">Hello, urban stakeholder 👋</div>
        <div class="hero-prompt">What should we understand around your MRT area?</div>
        <div class="notice">Synthetic demo data — not real Singapore measurements.</div>
        """,
        unsafe_allow_html=True,
    )
    _metric_strip(tool_count, station_count)


def _render_results(state: dict[str, Any]) -> None:
    st.markdown(
        '<div class="mobile-card card-lavender"><div class="section-label">Agent read</div><div class="card-title">How the question was interpreted</div></div>',
        unsafe_allow_html=True,
    )
    _pill_row(
        {
            "stakeholder": state.get("stakeholder_type"),
            "target": state.get("target_area"),
            "scenario": state.get("scenario_type"),
            "style": state.get("brief_style"),
        }
    )
    focus = ", ".join(state.get("analysis_focus", [])) or "None"
    st.caption(f"Focus: {focus}")

    st.markdown(
        '<div class="mobile-card card-yellow"><div class="section-label">01 Spatial Evidence</div><div class="card-title">Priority areas</div></div>',
        unsafe_allow_html=True,
    )
    priority_table = state.get("priority_table")
    _station_cards(priority_table)
    with st.expander("View full priority table"):
        st.dataframe(priority_table, use_container_width=True)

    st.markdown(
        '<div class="mobile-card card-mint"><div class="section-label">02 Scenario Evidence</div><div class="card-title">Intervention effect</div></div>',
        unsafe_allow_html=True,
    )
    scenario_result = state.get("scenario_result")
    if scenario_result is not None and not scenario_result.empty:
        _station_cards(scenario_result)
        with st.expander("View full scenario table"):
            st.dataframe(scenario_result, use_container_width=True)
    else:
        st.caption("No scenario result was generated.")

    st.markdown(
        '<div class="mobile-card card-brief"><div class="section-label">03 Generated Brief</div><div class="card-title">Planning brief</div></div>',
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.markdown(state.get("brief_text", ""))

    st.markdown(
        '<div class="mobile-card card-lavender"><div class="section-label">04 Evaluation</div><div class="card-title">Checks</div></div>',
        unsafe_allow_html=True,
    )
    evaluation = state.get("evaluation_result", {})
    checks = evaluation.get("checks", {}) if isinstance(evaluation, dict) else {}
    if checks:
        st.dataframe(
            pd.DataFrame([{"check": key, "passed": value} for key, value in checks.items()]),
            hide_index=True,
            use_container_width=True,
        )
        st.json({"passed": evaluation.get("passed"), "score": evaluation.get("score")})
    else:
        st.json(evaluation)

    st.markdown(
        '<div class="mobile-card card-dark"><div class="section-label">Behind the workflow</div><div class="card-title">Trace and tools</div></div>',
        unsafe_allow_html=True,
    )
    with st.expander("Trace steps"):
        st.json(state.get("trace_steps", []))
    with st.expander("Registered tools"):
        st.dataframe(_registered_tools_table(), hide_index=True, use_container_width=True)
    with st.expander("Raw final state preview"):
        st.json(_state_preview(state))


def _bottom_nav() -> None:
    st.markdown(
        """
        <div class="bottom-nav">
            <span>Ask</span>
            <span>Evidence</span>
            <span>Brief</span>
            <span>Trace</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="Everyday Access Planning Agent",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    _inject_styles()

    if "user_question" not in st.session_state:
        st.session_state["user_question"] = EXAMPLE_QUESTIONS[-1]

    station_count = len(load_station_area_indicators(str(DATA_PATH)))
    tool_count = len(list_tools())

    with st.sidebar:
        st.header("Examples")
        selected_example = st.radio("Question", EXAMPLE_QUESTIONS, label_visibility="collapsed")
        if st.button("Use selected example"):
            st.session_state["user_question"] = selected_example
            st.rerun()
        st.caption("Deterministic routing and tools. No LLM is called.")

    _render_static_shell(tool_count, station_count)
    _example_buttons()

    st.markdown(
        '<div class="mobile-card card-white"><div class="section-label">Ask</div><div class="card-title">Generate a planning brief</div></div>',
        unsafe_allow_html=True,
    )
    with st.form("planning_question_form"):
        user_question = st.text_area("Question", key="user_question", height=130)
        stakeholder_choice = st.selectbox(
            "Stakeholder override",
            ["auto", "citizen", "policy_maker", "researcher"],
            help="Use auto to let the deterministic router infer the stakeholder mode.",
        )
        submitted = st.form_submit_button("Generate Planning Brief")

    if submitted:
        if not user_question.strip():
            st.error("Please enter a planning question.")
        else:
            stakeholder_override = None if stakeholder_choice == "auto" else stakeholder_choice
            with st.spinner("Running deterministic planning workflow..."):
                state = run_planning_workflow(user_question.strip(), stakeholder_type=stakeholder_override)
            _render_results(state)
    else:
        st.info("Pick an example or write a question, then generate a deterministic planning brief.")

    _bottom_nav()


if __name__ == "__main__":
    main()