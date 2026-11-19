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
| **Member 1 (BHALLAMUDI VENKATA SRINIVAS KIRAN - 2025paml587@wilp.bits-pilani.ac.in)** | Data Architect & Reflex Agents | `schema.py`, `data/scenarios.json`, `agents/simple_reflex.py`, `agents/model_reflex.py`, `tests/test_member1.py`, `MEMBER1_NOTES.md` | ✅ Complete |
| **Member 2 (CHETAN RAGHAV - 2025paml605@wilp.bits-pilani.ac.in)** | Deliberative & Learning Agents | Three agents, experience history, Member 2 agent/UI tests, shared comparison and feedback integration, `MEMBER2_NOTES.md` | ✅ Days 2–5 complete; validation scope below |
| **Member 3 (SOURAV KUMAR - 2025paml606@wilp.bits-pilani.ac.in)** | LLM & LangChain Engineer | `tools/__init__.py`, `tools/incident_tools.py`, `agents/llm_agent.py`, `tests/test_member3.py`, `MEMBER3_NOTES.md` | ✅ Complete |
| **Member 4 (ANISHA PRAKASH DALSANIA - 2025paml574@wilp.bits-pilani.ac.in)** | UI Lead, Integration & Packaging | `app.py`, `requirements.txt`, `README.md`, end-to-end testing, screenshots | ✅ Complete |

The table retains the team's reported ownership/status. The Member 2 review on
19 November 2026 verified the agent and UI integration in offline fallback mode;
it does not certify live Ollama inference or screenshot/package completion.
See [Member 2 validation evidence](results/member2_validation.json).

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
├── requirements.txt            # Project dependencies
├── README.md                   # Complete system documentation & runbook
├── MEMBER1_NOTES.md            # Daily progress log & technical deliverables for Member 1
├── MEMBER2_NOTES.md            # Daily progress log & technical deliverables for Member 2
├── MEMBER3_NOTES.md            # Daily progress log & technical deliverables for Member 3
├── results/member2_validation.json  # Recorded Member 2 integration and learning results
└── tests/
    ├── test_member1.py         # Member 1 schema & edge-case check script
    ├── member2_fixtures.py     # Fixed synthetic history independent of live feedback
    ├── test_member2_agents.py  # Member 2 deliberative & learning suite (20 tests)
    ├── test_member2_ui.py      # Member 2 Streamlit integration suite (7 tests)
    ├── test_member3.py         # Member 3 tools, LLM, and pipeline suite (13 tests)
    └── test_e2e_integration.py # Six-agent schema/execution check script
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
  $$\text{Goals: } \text{service\_status} = \text{RUNNING}, \quad \text{error\_rate\_percent} < 1.0\%, \quad \text{latency\_ms} < 200\text{ms}$$
- **Decision:** Selects the first feasible plan predicted to satisfy all SLA goals.
- **Limitation:** Single-step, hand-authored recovery predictions. Feasible plans are not ranked by risk or cost. Predictions are teaching assumptions, not observed recovery guarantees.

### 4. Utility-Based Agent (`agents/utility_based.py`)
- **Mechanism:** Solves multi-objective trade-offs using a quantitative utility scoring formula:
  $$U(a) = 0.50 \cdot \text{Speed}(a) + 0.30 \cdot \text{Safety}(a) - 0.20 \cdot \text{Cost}(a)$$
- **Decision:** Speed, safety, and cost ratings each use a 0–100 scale. The agent selects the highest utility among plans predicted to meet all SLA goals; utility itself is not a percentage (the default formula has theoretical range −20 to 80).
- **Limitation:** Ratings and weights are subjective and static. Scaling assumes spare capacity and caching assumes cacheable requests. High-scoring actions that do not meet the modeled SLA are excluded.

### 5. Learning Agent (`agents/learning_agent.py`)
- **Mechanism:** Ranks eligible actions using per-scenario success/failure counts and a smoothed Bayesian estimate:
  $$\hat{P}(\text{Success} \mid s, a) = \frac{\text{success} + 1}{\text{success} + \text{failure} + 2}$$
- **Adaptability:** Persists experience in `data/experience.json`. When operators record observed incident outcomes, the agent updates counts and shifts future recommendations.
- **Feedback contract:** `analyze()` only recommends. `record_outcome()` records one explicit observed or simulated outcome. The shipped counts are synthetic demonstration history. `feedback_actions(scenario)` supplies the UI's eligible action keys and descriptions; passing `scenario=` to `record_outcome()` validates that the action is eligible for that scenario.
- **Limitation:** No exploration/problem-generator mechanism or causal learning. Cold starts use equal priors and candidate order; small or biased samples can mislead. Atomic JSON writes assume one writer and do not deduplicate repeated outcome submissions.

### 6. LLM Agent with Tool Calling (`agents/llm_agent.py`)
- **Mechanism:** ReAct pattern using local Ollama (`qwen2.5:3b`, `qwen3:4b`, or `llama3.2`) integrated via `langchain_ollama.ChatOllama` with native tool binding (`.bind_tools()`).
- **Tools Invoked:**
  1. `get_metrics(scenario_key)`: Telemetry inspection (CPU, latency, error rate, DB pool).
  2. `search_logs(scenario_key, query="")`: Log pattern matching (e.g. `psycopg2.pool.PoolError`).
  3. `get_deployment_history(scenario_key)`: Pipeline commits and configuration changes.
  4. `check_previous_version(scenario_key)`: Prior build release tag and health status.
- **Tool path and verification:** Includes tool binding and a deterministic offline fallback that executes the investigation tools. The Member 2 integration run verified the fallback and report contract. Actual model-driven tool selection and grounding must be verified separately by Member 3; fallback success does not certify live inference.

---

## 5. Comparative Evaluation Across Shared Scenarios

All six agents use the shared scenarios in `data/scenarios.json`. The following
comparison uses the shipped synthetic learning history and default utility
weights. The LLM column describes the tested deterministic offline fallback;
online model outputs and tool choices can differ and require separate validation.

| Scenario | Title & Telemetry | Simple Reflex | Model-Based | Goal-Based | Utility-Based | Learning Agent | LLM agent: tested offline fallback |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Normal_Baseline** | CPU 28%, latency 45ms, DB 18%, RUNNING | No action; monitor | Maintain baseline state | Goals met; monitor | Monitor (**80.00**) | Monitor (**11/12** estimate) | Monitor |
| **Scenario A** | Latency 4200ms, errors 38.5%, DB pool 100/100 after analytics patch | Flush DB connections and raise pool limit | Roll back patch and drain pool | Roll back patch to v2.1.0 and drain connections | Same plan (**65.50**) | Same plan (**5/6** estimate) | Roll back patch, reset pool, drain connections |
| **Scenario B** | CPU 94%, RPS 980, DB pool 32/100 | Scale replicas | Auto-scale and enable edge rate limiting | Scale replicas (first feasible plan) | **Scale plus caching (57.00)** versus scaling alone (55.50) | **Scale replicas (6/7)** versus scale plus caching (3/5) | Scale, cache, and rate-limit |
| **Scenario C** | DOWN, CPU 5%, errors 100%, config parse error | Restart container | Roll back config/release to v2.1.0 | Roll back config/release to v2.1.0 | Same plan (**69.00**) | Same plan (**7/8** estimate) | Roll back config/deployment and validate YAML |

The fallback executes all four tools on each shared scenario. Its successful
execution is not evidence that a live model made tool calls.

### Why the decisions differ

1. **Reflex versus context (Scenario C):** The simple reflex agent reacts to the outage by restarting. The model-based agent considers deployment context and recommends rollback. Restarting alone may leave the configuration error unresolved.
2. **Goal satisfaction versus utility (Scenario B):** The goal agent accepts the first plan predicted to recover the SLA. Utility prefers scaling plus caching because its assumed lower cost outweighs its lower speed and safety ratings. Strict rate limiting is excluded because its predicted 5% errors violate the goal.
3. **History versus static ratings:** Learning initially favors scaling alone because of its stronger synthetic history. After five explicit scale-out failures, its estimate changes from `6/7` to `6/12`, below caching's `3/5`; the preference changes and survives reloading the history file. These estimates are smoothed probabilities, not raw historical win rates.
4. **Limits of the evidence:** Classical decisions use predefined models, which can also inspect logs and deployment data. Utility ratings and recovery predictions are illustrative. The learning agent only learns action preferences within its eligible candidates. Reports expose these limitations for all agents.

### Learning feedback demonstration

1. Select **Scenario_B**, then click **Run All 6 AI Agents**.
2. In the feedback simulator, select **Horizontally scale service replicas...**.
3. Starting from the shipped history, click **Record Failure** five times, representing five separate simulated outcomes. The history, learning report, and comparison row refresh after each click; the other agents are not rerun.
4. The learning recommendation changes to **Scale service replicas and enable caching...**. Running analysis or reloading the page does not create additional outcomes.

Feedback options come from the selected scenario's eligible candidates, including
monitoring for Normal_Baseline and rollback/drain for Scenario_A. Switching the
scenario or model clears the previous reports until another analysis is run.
Each feedback click intentionally persists one event; repeated clicks count as
multiple outcomes. If the history has already changed, use the automated Member 2
tests for a reproducible demonstration with isolated fixtures.

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
# Run individual members' checks:
python -m tests.test_member1
python -m tests.test_member2_agents
python -m tests.test_member2_ui
python -m tests.test_member3

# Run all discoverable tests, including Member 2's Streamlit UI checks:
python -m unittest discover -s tests -v
```

Member 2 validation on **19 November 2026**, Python **3.12.3**: **40 unittest
tests passed** (20 Member 2 agent tests, 7 Member 2 UI tests, 13 Member 3 tests).
The separate Member 1 script passed 10 agent/scenario checks and the six-agent
script passed all 24 report checks across four scenarios. Those two scripts are
not executed by unittest discovery; run their module commands explicitly.

The recorded run forced Ollama availability offline and exercised the real tools
and fallback. Member 2 UI tests always use that mode and temporary history;
other tests may use a live model when one is available. AppTest checks Streamlit
interactions without a browser. Live inference, browser screenshots, and visual
review remain separate demo checks. See [recorded results and package versions](results/member2_validation.json).
The repository's dependency file remains unpinned.

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
- [x] **Offline six-agent integration:** All report schemas and the fallback tool path verified across the four shared scenarios.
- [ ] **Live Ollama demonstration:** Members 3/4 must verify actual model-driven tool calls and evidence-grounded output; offline fallback results do not establish this.
- [x] **Shared Scenario Telemetry:** All 6 agents receive identical scenario inputs from `data/scenarios.json`.
- [x] **Streamlit UI:** `app.py` allows selecting scenarios, running all 6 agents, viewing the side-by-side comparison table, and simulating learning feedback live.
- [x] **Learning Experience Persistence:** `data/experience.json` tracks outcome counts and adapts policy dynamically.
- [x] **Documentation & Deliverables:** Comprehensive `README.md`, `requirements.txt`, individual member notes (`MEMBER1_NOTES.md`, `MEMBER2_NOTES.md`, `MEMBER3_NOTES.md`), and passing test suites.

---

Live demo screenshots and final packaging remain with Members 3/4. The checked
integration items above describe the recorded automated validation, not a claim
that those final submission artifacts have been produced in this review.
