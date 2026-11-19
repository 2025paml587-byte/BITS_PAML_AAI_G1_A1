# Intelligent Production Incident Management System
**Course:** Agentic AI (PAML / AGAI Assignment 1 - Set 1)  
**Team:** Group 1  
**GitHub Repository:** [2025paml587-byte/BITS_PAML_AAI_G1_A1](https://github.com/2025paml587-byte/BITS_PAML_AAI_G1_A1)

---

## 1. Executive Summary & Problem Statement

Modern Site Reliability Engineering (SRE) demands automated, resilient incident triage when critical microservices experience latency spikes, connection pool saturations, CPU bottlenecks, or post-deployment crash loops.

This project implements an **Intelligent Production Incident Management Assistant** in Python. The system feeds identical scenario telemetry into **six distinct AI agent architectures** (five classical agent formalisms rooted in Russell & Norvig's AI taxonomy and one tool-calling LLM powered by a local Ollama model) and renders their root-cause diagnoses, recovery recommendations, and comparative reasoning in an interactive **Streamlit dashboard**.

---

## 2. Team Work Partition & Ownership

| Member | Role | Owned Files & Deliverables | Status |
| :--- | :--- | :--- | :---: |
| **Member 1 (Kiran)** | Data Architect & Reflex Agents | `schema.py`, `data/scenarios.json`, `agents/simple_reflex.py`, `agents/model_reflex.py`, `tests/test_member1.py`, `MEMBER1_NOTES.md` | ✅ Complete |
| **Member 2 (Chetan)** | Deliberative & Learning Agents | `agents/goal_based.py`, `agents/utility_based.py`, `agents/learning_agent.py`, `data/experience.json`, `tests/test_member2_agents.py`, `MEMBER2_NOTES.md` | ✅ Complete |
| **Member 3 (Sourav)** | LLM & LangChain Engineer | `tools/__init__.py`, `tools/incident_tools.py`, `agents/llm_agent.py`, `tests/test_member3.py`, `MEMBER3_NOTES.md` | ✅ Complete |
| **Member 4 (Anisha)** | UI Lead, Integration & Packaging | `app.py`, `requirements.txt`, `README.md`, end-to-end testing, screenshots | ✅ Complete |

---

## 3. System Architecture & Directory Structure

```text
incident-management-ai/
├── data/
│   ├── scenarios.json          # Shared telemetry, logs, and deployment data for all 4 scenarios
│   └── experience.json         # Persistent JSON experience memory tracking success/failure counts
├── agents/
│   ├── __init__.py
│   ├── simple_reflex.py        # 1. Simple Reflex Agent (Stateless condition-action rules)
│   ├── model_reflex.py         # 2. Model-Based Reflex Agent (Baseline state tracking & deploy delta)
│   ├── goal_based.py           # 3. Goal-Based Agent (SLA target state satisfaction search)
│   ├── utility_based.py        # 4. Utility-Based Agent (Multi-attribute utility optimization)
│   ├── learning_agent.py       # 5. Learning Agent (Bayesian smoothed outcome history)
│   └── llm_agent.py            # 6. LLM Incident Agent (Local Ollama via LangChain + Tool Calling)
├── tools/
│   ├── __init__.py
│   └── incident_tools.py       # 4 LangChain @tool functions: get_metrics, search_logs, get_deployment_history, check_previous_version
├── schema.py                   # Standardized 7-key AgentReport TypedDict & format_report helper
├── app.py                      # Interactive Streamlit Web Dashboard
├── requirements.txt            # Pinned project dependencies
├── README.md                   # Complete system documentation & runbook
├── MEMBER1_NOTES.md            # Daily progress log & technical deliverables for Member 1
├── MEMBER2_NOTES.md            # Daily progress log & technical deliverables for Member 2
├── MEMBER3_NOTES.md            # Daily progress log & technical deliverables for Member 3
└── tests/
    ├── test_member1.py         # Member 1 unit & edge-case test suite
    ├── test_member2_agents.py  # Member 2 deliberative & learning test suite (17 tests)
    └── test_member3.py         # Member 3 tools, LLM agent, and pipeline integration suite (13 tests)
```

---

## 4. The Six Agent Architectures

### 1. Simple Reflex Agent (`agents/simple_reflex.py`)
- **Mechanism:** Condition-action rules mapping immediate percepts directly to corrective actions ($f(p) \rightarrow a$) without internal state or historical context.
- **Rule Triggers:** `CRASH_LOOP` $\rightarrow$ restart container; `DB pool exhausted` $\rightarrow$ flush pool & raise limit; `CPU > 85%` $\rightarrow$ scale out.
- **Limitation:** Stateless. Ignores deployment history, error logs, and root causes. On Scenario C, blindly restarts a container crashing from a config syntax error, causing an infinite crash loop.

### 2. Model-Based Reflex Agent (`agents/model_reflex.py`)
- **Mechanism:** Maintains an internal model of healthy baseline telemetry (`CPU: 30%`, `RPS: 130`, `Latency: 50ms`, `DB: 25%`) and correlates changes against `deployment_history`.
- **Advantage:** Differentiates between organic traffic surges ($7.3\times$ baseline with healthy DB) and internal query deadlocks. On Scenario C, detects the recent `config.yaml` update and recommends rolling back to `v2.1.0`.

### 3. Goal-Based Agent (`agents/goal_based.py`)
- **Mechanism:** Evaluates candidate recovery plans against explicit target SLA goals:
  $$\text{Goals: } \text{service\_status} = \text{RUNNING}, \quad \text{error\_rate} < 1.0\%, \quad \text{latency\_p95} < 200\text{ms}$$
- **Decision:** Selects the first feasible plan predicted to satisfy all SLA goals.

### 4. Utility-Based Agent (`agents/utility_based.py`)
- **Mechanism:** Solves multi-objective trade-offs using a quantitative utility scoring formula:
  $$U(a) = 0.50 \cdot \text{Speed}(a) + 0.30 \cdot \text{Safety}(a) - 0.20 \cdot \text{Cost}(a)$$
- **Decision:** Compares all candidate recovery plans on a $0-100$ scale and selects the action maximizing expected utility $a^* = \arg\max_a U(a)$.

### 5. Learning Agent (`agents/learning_agent.py`)
- **Mechanism:** Four-component architecture (Critic, Learning Element, Performance Element, Problem Generator). Ranks eligible actions using smoothed Bayesian outcome estimates:
  $$\hat{P}(\text{Success} \mid s, a) = \frac{\text{success} + 1}{\text{success} + \text{failure} + 2}$$
- **Adaptability:** Persists experience in `data/experience.json`. When operators record observed incident outcomes, the agent updates counts and shifts future recommendations.

### 6. LLM Agent with Tool Calling (`agents/llm_agent.py`)
- **Mechanism:** ReAct pattern using local Ollama (`qwen2.5:3b`, `qwen3:4b`, or `llama3.2`) integrated via `langchain_ollama.ChatOllama` with native tool binding (`.bind_tools()`).
- **Tools Invoked:**
  1. `get_metrics(scenario_key)`: Telemetry inspection (CPU, latency, error rate, DB pool).
  2. `search_logs(scenario_key, query="")`: Log pattern matching (e.g. `psycopg2.pool.PoolError`).
  3. `get_deployment_history(scenario_key)`: Pipeline commits and configuration changes.
  4. `check_previous_version(scenario_key)`: Prior build release tag and health status.
- **Enforcement & Grounding:** Enforces $\ge 2$ tool invocations before synthesizing conclusions, strictly citing tool observations as evidence. Includes a deterministic offline fallback emulator to ensure tests and UI never crash if Ollama is paused.

---

## 5. Comparative Evaluation Across Shared Scenarios

All six agents process the exact same scenario telemetry from `data/scenarios.json`:

| Scenario | Title & Telemetry | Simple Reflex | Model-Based | Goal-Based | Utility-Based | Learning Agent | LLM Agent (Ollama) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Normal** | CPU 28%, Latency 45ms, DB 18%, Status RUNNING | No action; monitor | Matches baseline; monitor | Goals met; monitor | Monitor (Utility: 100) | Monitor (Cold start priors) | Calls `get_metrics` & `search_logs`; confirms nominal state; monitor |
| **Scenario A** | Latency 4200ms, 38.5% 503s, DB pool 100/100 after analytics patch | Resets DB pool only | Correlates deploy; rolls back patch & drains pool | Rollback patch + restart pool to restore SLA | Rollback + drain pool (Balances speed & risk) | Rollback + drain pool (5/6 historical success) | Calls `get_metrics` & `search_logs`; catches `PoolError`; rolls back patch & drains connections |
| **Scenario B** | CPU 94%, RPS 980 ($7.5\times$), DB pool 32% (Healthy) | Scales replicas (CPU > 85%) | Detects $7.5\times$ traffic surge with healthy DB; auto-scales | Scale replicas (First plan satisfying SLA) | **Scale + Caching** (Score: 57.0 vs 55.5 due to cost advantage) | **Scale replicas** (Score: 6/7 historical success vs 3/5) | Calls `get_metrics` & `search_logs`; detects traffic spike with normal DB; recommends auto-scaling + rate limiting |
| **Scenario C** | Status CRASH_LOOP, CPU 5%, Errors 100%, config parse error | Blindly restarts container (Infinite crash loop!) | Correlates config change; rolls back to `v2.1.0` | Rollback config to `v2.1.0` to reach `RUNNING` goal | Rollback config to `v2.1.0` (Safest path) | Rollback config to `v2.1.0` (7/8 historical success) | Calls `search_logs` & `get_deployment_history`; identifies invalid YAML key `DB_TIMEOUT_MS`; rolls back to `v2.1.0` |

---

## 6. Setup & Execution Runbook

### Prerequisites
* Python 3.10+ (tested on Python 3.13)
* [Ollama](https://ollama.com) installed locally with `qwen2.5:3b` (or `qwen3:4b`) pulled:
  ```bash
  ollama pull qwen2.5:3b
  ```
* Git

### Step 1: Clone Repository & Create Virtual Environment
1. Clone the repository and enter the project directory:
   ```bash
   git clone https://github.com/2025paml587-byte/BITS_PAML_AAI_G1_A1.git
   cd BITS_PAML_AAI_G1_A1
   ```

# Create and activate virtual environment
   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .\.venv\Scripts\Activate.ps1
   # macOS/Linux:
   source .venv/bin/activate
   ```

### Step 2: Install Dependencies
 ```bash
   pip install -r requirements.txt
   ```

### Step 3: (Optional) Pull Local Ollama Model
```bash
ollama pull qwen2.5:3b
```

### Step 4: Run the Complete Unit & Integration Test Suite
```bash
# Run Member 1 tests:
python -m tests.test_member1
python -m tests.test_member2_agents
python -m tests.test_member3

# Run Member 2 and Member 3 discovery suite (30 tests):
python -m unittest discover -s tests -v
```
*All 40 unit and integration tests pass with 100% schema compliance.*

### Step 5: Run automated end-to-end verification tests:
   ```bash
   python -m tests.test_e2e_integration
   ```

### Step 6: Launch the Streamlit Web Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501` to explore the interactive incident management dashboard!

---

## 7. Submission Checklist Verification

- [x] **Five Classical Agents:** `simple_reflex.py`, `model_reflex.py`, `goal_based.py`, `utility_based.py`, `learning_agent.py` each correctly implement their intended decision paradigm.
- [x] **LLM Agent & Tool Calling:** `llm_agent.py` invokes $\ge 2$ tools (`incident_tools.py`) via LangChain and grounds recommendations in observations.
- [x] **Shared Scenario Telemetry:** All 6 agents receive identical scenario inputs from `data/scenarios.json`.
- [x] **Streamlit UI:** `app.py` allows selecting scenarios, running all 6 agents, viewing the side-by-side comparison table, and simulating learning feedback live.
- [x] **Learning Experience Persistence:** `data/experience.json` tracks outcome counts and adapts policy dynamically.
- [x] **Documentation & Deliverables:** Comprehensive `README.md`, `requirements.txt`, individual member notes (`MEMBER1_NOTES.md`, `MEMBER2_NOTES.md`, `MEMBER3_NOTES.md`), and passing test suites.

---

## 2. Why Agent Decisions Differ (Comparative Evaluation)

| Scenario | Simple Reflex | Model-Based Reflex | Goal-Based | Utility-Based | Learning Agent | LLM Agent (Ollama) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Normal_Baseline** | Monitor (no action) | Maintain baseline state | No intervention (SLAs met) | Continue monitoring (Utility: 95) | No action (100% win rate) | No action required |
| **Scenario_A** (DB Pool Exhausted) | Flush DB pool & raise limit | Rollback patch to `v2.1.0` & drain pool | Rollback patch + restart pool | Rollback & recycle pool (Utility: 89) | Rollback patch & drain pool | Rollback `v2.1.1` analytics patch |
| **Scenario_B** (Edge: High CPU/Traffic, Normal DB) | Scale out replicas | Auto-scale + edge rate limiting | Auto-scale 2 -> 6 pods | Horizontal auto-scale + cache (Utility: 86) | Horizontal auto-scale | Scale workers horizontally |
| **Scenario_C** (Startup Crash after Config Change) | Restart container *(suboptimal)* | Rollback config to `v2.1.0` | Rollback to healthy `v2.1.0` | Rollback to previous version (Utility: 92) | Rollback config to `v2.1.0` | Revert invalid `DB_POOL_MODE` in `config.yaml` |

### Key Analytical Takeaways
1. **Stateless Reaction vs. State Tracking (Scenario C):** The *Simple Reflex Agent* only perceives `service_status=DOWN` and recommends restarting the container, which fails repeatedly when a configuration file is invalid. The *Model-Based Reflex Agent* compares current state against its healthy baseline and correlates the crash with `deployment_history`, safely recommending a rollback.
2. **Goal Satisfaction vs. Multi-Attribute Utility (Scenario B):** While the *Goal-Based Agent* treats any SLA-restoring plan equally, the *Utility-Based Agent* balances **Speed, Safety, and Cost**, selecting horizontal auto-scaling over harsh rate-limiting to preserve user traffic.
3. **Empirical Adaptation (`experience.json`):** The *Learning Agent* queries historical success/failure counts and increments outcome records after each execution, reinforcing proven fixes over actions that failed in past incidents.
4. **Unstructured Evidence Synthesis (LLM + Tools):** Unlike classical agents restricted to structured metrics, the *LLM Agent* dynamically calls `get_metrics`, `search_logs`, `get_deployment_history`, and `check_previous_version` to extract specific log errors (such as invalid config keys) and ground its recovery plan in live tool evidence.