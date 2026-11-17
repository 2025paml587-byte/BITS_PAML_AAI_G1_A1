"""Intelligent Production Incident Management System - Streamlit Dashboard.

Integrates all 6 SRE incident response agents:
1. Simple Reflex Agent (Stateless condition-action rules)
2. Model-Based Reflex Agent (Internal baseline tracking & deploy delta)
3. Goal-Based Agent (SLA recovery satisfaction search)
4. Utility-Based Agent (Multi-attribute scoring: Speed vs Safety vs Cost)
5. Learning Agent (Outcome history / Q-score reinforcement)
6. LLM Incident Agent (Local Ollama with LangChain Tool Calling)
"""

from __future__ import annotations

import json
from pathlib import Path
import pandas as pd
import streamlit as st

from agents.goal_based import GoalBasedAgent
from agents.learning_agent import DEFAULT_EXPERIENCE, LearningAgent
from agents.llm_agent import LLMIncidentAgent, is_ollama_reachable
from agents.model_reflex import ModelBasedReflexAgent
from agents.simple_reflex import SimpleReflexAgent
from agents.utility_based import UtilityBasedAgent

# Page configuration
st.set_page_config(
    page_title="AI SRE Incident Commander",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Paths
ROOT = Path(__file__).resolve().parent
SCENARIOS_PATH = ROOT / "data" / "scenarios.json"
EXPERIENCE_PATH = ROOT / "data" / "experience.json"


@st.cache_data
def load_scenarios():
    with open(SCENARIOS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_experience_data():
    if EXPERIENCE_PATH.is_file():
        try:
            return json.loads(EXPERIENCE_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


scenarios = load_scenarios()

# Sidebar controls
st.sidebar.title("🚨 SRE Incident Control")
st.sidebar.markdown("---")

selected_key = st.sidebar.selectbox(
    "Select Incident Scenario",
    options=list(scenarios.keys()),
    format_func=lambda k: f"{k}: {scenarios[k]['title'][:32]}...",
)
scenario = scenarios[selected_key]

model_choice = st.sidebar.selectbox(
    "Local Ollama Model",
    options=["qwen2.5:3b", "qwen3:4b", "llama3.2", "qwen2.5:7b"],
    index=0,
    help="Select the local model running in Ollama on localhost:11434.",
)

ollama_online = is_ollama_reachable()
if ollama_online:
    st.sidebar.success("🟢 Local Ollama Service: Online")
else:
    st.sidebar.warning("🟡 Local Ollama Service: Offline (Using Grounded Fallback)")

st.sidebar.markdown("---")
st.sidebar.markdown("### Agent Framework Taxonomy")
st.sidebar.markdown(
    """
    - **Simple Reflex:** Immediate condition-action thresholds
    - **Model-Based:** Tracks healthy baseline & deploy deltas
    - **Goal-Based:** Explores plans meeting SLA targets
    - **Utility-Based:** Multi-attribute utility optimization
    - **Learning:** Contextual Bayesian outcome reinforcement
    - **LLM Agent:** Tool-calling ReAct investigation (Ollama)
    """
)

# Main Dashboard Header
st.title("🚨 Intelligent Production Incident Management System")
st.caption("Benchmarking Classical AI Agents & Tool-Augmented LLM on Production SRE Telemetry")

# Telemetry Overview Card
st.markdown(f"### Active Incident: **{scenario['title']}**")
col_cat, col_status = st.columns([3, 1])
with col_cat:
    st.info(f"**Incident Category:** {scenario.get('category', 'Critical')} | **Scenario Key:** `{selected_key}`")
with col_status:
    m = scenario["metrics"]
    srv_status = m.get("service_status", "UNKNOWN")
    if srv_status == "RUNNING":
        st.success(f"Status: **{srv_status}**")
    elif srv_status == "DEGRADED":
        st.warning(f"Status: **{srv_status}**")
    else:
        st.error(f"Status: **{srv_status}**")

# Metrics Gauges
m_cols = st.columns(6)
m_cols[0].metric("CPU Utilization", f"{m.get('cpu_percent', 0)}%")
m_cols[1].metric("P95 Latency", f"{m.get('latency_ms', 0)} ms")
m_cols[2].metric("Error Rate", f"{m.get('error_rate_percent', 0.0)}%")
m_cols[3].metric("Request Rate", f"{m.get('requests_per_sec', 0)} rps")
m_cols[4].metric(
    "DB Pool Active",
    f"{m.get('db_active_connections', 0)} / {m.get('db_max_connections', 100)}",
)
dep = scenario.get("deployment_history", {})
m_cols[5].metric("Current Version", dep.get("current_version", "unknown"))

# Logs & Deployment Accordions
with st.expander("🔍 View Raw Scenario Telemetry, Logs & Deployment History", expanded=False):
    t_tab1, t_tab2, t_tab3 = st.tabs(["Recent Application Logs", "Deployment History", "Previous Build Health"])
    with t_tab1:
        for log_line in scenario.get("logs", []):
            if "ERROR" in log_line or "FATAL" in log_line:
                st.error(log_line)
            elif "WARN" in log_line:
                st.warning(log_line)
            else:
                st.text(log_line)
    with t_tab2:
        st.json(dep)
    with t_tab3:
        st.json(scenario.get("previous_version", {}))

st.markdown("---")

# Execution Button
run_clicked = st.button("⚡ Run All 6 AI Agents Simultaneously", type="primary", use_container_width=True)

if run_clicked or "last_reports" in st.session_state:
    if run_clicked:
        with st.spinner("Executing agent decision pipelines across all 6 architectures..."):
            reports = [
                SimpleReflexAgent().analyze(scenario),
                ModelBasedReflexAgent().analyze(scenario),
                GoalBasedAgent().analyze(scenario),
                UtilityBasedAgent().analyze(scenario),
                LearningAgent().analyze(scenario, scenario_key=selected_key),
            ]

            llm_agent = LLMIncidentAgent(model_name=model_choice)
            llm_report, tools_used = llm_agent.analyze(selected_key, scenario["title"])
            reports.append(llm_report)

            st.session_state["last_reports"] = reports
            st.session_state["tools_used"] = tools_used
            st.session_state["active_key"] = selected_key
    else:
        reports = st.session_state["last_reports"]
        tools_used = st.session_state.get("tools_used", [])

    st.success(f"✅ All 6 agents successfully completed diagnostic evaluation on `{selected_key}`!")

    # 1. Comparative Decision Matrix
    st.subheader("📊 Cross-Agent Comparative Decision Matrix")
    df_data = []
    agent_categories = [
        "Simple Reflex (Stateless Rules)",
        "Model-Based Reflex (State Tracking)",
        "Goal-Based (SLA Satisfaction)",
        "Utility-Based (Multi-Objective Optimization)",
        "Learning Agent (Bayesian Outcome Memory)",
        f"LLM Agent ({model_choice} + Tool Calling)",
    ]

    for idx, r in enumerate(reports):
        df_data.append(
            {
                "Agent Architecture": r["agent_name"],
                "Decision Mechanism": agent_categories[idx] if idx < len(agent_categories) else "AI Agent",
                "Likely Root Cause": r["likely_cause"],
                "Recommended Action": r["recommended_action"],
                "Architectural Limitations": r["limitations"],
            }
        )

    df_comparison = pd.DataFrame(df_data)
    st.dataframe(df_comparison, use_container_width=True)

    # 2. Detailed Expandable Reports for Each Agent
    st.subheader("📑 Detailed Agent Investigation Reports")
    agent_tabs = st.tabs([r["agent_name"] for r in reports])

    for idx, r in enumerate(reports):
        with agent_tabs[idx]:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"#### **{r['agent_name']}**")
                st.markdown(f"**Incident Summary:** {r['incident_summary']}")
                st.markdown(f"**Likely Root Cause:** `{r['likely_cause']}`")
                st.success(f"**Recommended Recovery Action:**\n\n{r['recommended_action']}")

            with col2:
                st.markdown("##### **Verification Steps**")
                for step in r["verification_steps"]:
                    st.markdown(f"- ✅ {step}")

                st.markdown("##### **Evidence Gathered**")
                for ev in r["evidence"]:
                    st.markdown(f"- 📌 {ev}")

            st.warning(f"**Known Agent Limitations:** {r['limitations']}")

    # 3. Interactive LLM Tool Execution Visualizer
    st.markdown("---")
    st.subheader("🛠️ LLM Tool Calling Inspector (ReAct Observability)")
    st.markdown(
        f"The local LLM (`{model_choice}`) actively invoked **{len(tools_used)} tool(s)** to ground its incident response:"
    )
    t_cols = st.columns(len(tools_used) if tools_used else 1)
    if tools_used:
        for idx, tool_call in enumerate(tools_used):
            with t_cols[idx]:
                st.code(tool_call, language="python")
    else:
        st.info("No external tools called.")

    # 4. Interactive Learning Agent Feedback Loop
    st.markdown("---")
    st.subheader("🧠 Learning Agent Feedback Simulator")
    st.markdown(
        "Demonstrate how the **Learning Agent** updates its persistent experience data (`experience.json`) "
        "and dynamically adapts future decisions based on observed incident resolution outcomes."
    )

    exp_data = load_experience_data()
    scenario_history = exp_data.get(selected_key, {})

    hist_col1, hist_col2 = st.columns([2, 1])
    with hist_col1:
        st.markdown(f"**Current Historical Outcome Records for `{selected_key}`:**")
        if scenario_history:
            st.json(scenario_history)
        else:
            st.info("No prior history recorded for this scenario yet. Cold start priors will apply.")

    with hist_col2:
        st.markdown("**Simulate Incident Action Outcome:**")
        learning_agent = LearningAgent()
        eligible_actions = ["scale_out", "rollback_patch", "rollback_config", "scale_and_cache", "restart_pool"]

        action_to_feedback = st.selectbox("Select Action to Feedback:", eligible_actions)
        f_col_succ, f_col_fail = st.columns(2)

        if f_col_succ.button("👍 Record Success", use_container_width=True):
            learning_agent.record_outcome(selected_key, action_to_feedback, success=True)
            st.success(f"Recorded SUCCESS for '{action_to_feedback}'! Experience updated.")
            st.rerun()

        if f_col_fail.button("👎 Record Failure", use_container_width=True):
            learning_agent.record_outcome(selected_key, action_to_feedback, success=False)
            st.error(f"Recorded FAILURE for '{action_to_feedback}'! Policy updated.")
            st.rerun()

st.markdown("---")
st.caption("Intelligent Production Incident Management System | Group 1 | BITS Pilani PAML / AGAI")
