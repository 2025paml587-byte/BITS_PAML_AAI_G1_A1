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
As part of Member 4's work, we used Ollama, pulled `qwen2.5:3b`,
and verified live model-driven tool calls and 24/24 six-agent schema checks
online (see [Member 4 implementation notes](MEMBER4_NOTES.md)); `requirements.txt`
is now pinned and `screenshots/` now contains captured evidence for all 4
scenarios plus an agent tab, the tool inspector, and the feedback simulator.
See [Member 2 validation evidence](results/member2_validation.json).

---

## 3. System Architecture & Directory Structure

```text
incident-management-ai/
├── data/
│   ├── scenarios.json               # Shared telemetry, logs, and deployment data for all 4 scenarios
│   └── experience.json              # Persistent JSON experience memory tracking success/failure counts
├── agents/
│   ├── __init__.py
│   ├── simple_reflex.py             # 1. Simple Reflex Agent (Stateless condition-action rules)
│   ├── model_reflex.py              # 2. Model-Based Reflex Agent (Baseline state tracking & deploy delta)
│   ├── goal_based.py                # 3. Goal-Based Agent (SLA target state satisfaction search)
│   ├── utility_based.py             # 4. Utility-Based Agent (Multi-attribute utility optimization)
│   ├── learning_agent.py            # 5. Learning Agent (Bayesian smoothed outcome history)
│   └── llm_agent.py                 # 6. LLM Incident Agent (Local Ollama via LangChain + Tool Calling)
├── tools/
│   ├── __init__.py
│   └── incident_tools.py            # 4 LangChain @tool functions: get_metrics, search_logs, get_deployment_history, check_previous_version
├── schema.py                        # Standardized 7-key AgentReport TypedDict & format_report helper
├── app.py                           # Interactive Streamlit dashboard integrating all 6 agents (Member 4)
├── requirements.txt                 # Pinned project dependencies (Member 4)
├── README.md                        # Complete system documentation & runbook
├── MEMBER1_NOTES.md                 # Daily progress log & technical deliverables for Member 1
├── MEMBER2_NOTES.md                 # Daily progress log & technical deliverables for Member 2
├── MEMBER3_NOTES.md                 # Daily progress log & technical deliverables for Member 3
├── MEMBER4_NOTES.md                 # Daily progress log & technical deliverables for Member 4
├── UI.pdf                           # Exported PDF snapshot of the live Streamlit dashboard (Member 4)
├── results/
│   └── member2_validation.json      # Recorded Member 2 integration and learning results
├── screenshots/                     # Captured UI evidence across all 4 scenarios (Member 4)
│   ├── Baseline.PNG                         # Normal_Baseline: telemetry + comparison table
│   ├── Scenario-A.PNG                       # Scenario_A: telemetry + comparison table, Ollama online badge
│   ├── Scenario-B.PNG                       # Scenario_B: telemetry + comparison table, Ollama online badge
│   ├── Scenario-C.PNG                       # Scenario_C: telemetry + comparison table, Ollama online badge
│   ├── Scenario-B-LLM-Agent-Tab.png         # Expanded LLM Agent tab: evidence, tool outputs, limitations
│   ├── Scenario-B-ToolInspector.png         # LLM Tool Calling Inspector: live tool-call trace
│   ├── Scenario-B-FeedbackSimulator-Before.png  # Learning history before a recorded outcome
│   └── Scenario-B-FeedbackSimulator-After.png   # Learning history after recording one failure
└── tests/
    ├── test_member1.py              # Member 1 schema & edge-case check script
    ├── member2_fixtures.py          # Fixed synthetic history independent of live feedback
    ├── test_member2_agents.py       # Member 2 deliberative & learning suite (20 tests)
    ├── test_member2_ui.py           # Member 2 Streamlit integration suite (7 tests)
    ├── test_member3.py              # Member 3 tools, LLM, and pipeline suite (13 tests)
    ├── test_member4.py              # Member 4 packaging suite: pinned deps, screenshots, app smoke test (7 tests)
    └── test_e2e_integration.py      # Six-agent schema/execution check script
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
- **Tool path and verification:** Includes tool binding and a deterministic offline fallback that executes the investigation tools. The Member 2 integration run verified the fallback and report contract. On 20 November 2026, Member 4 verified live model-driven tool calls with `qwen2.5:3b` across all 4 scenarios (2-4 real tool calls per scenario, 24/24 schema checks). **Known issue (reported to Member 3, not yet fixed):** `ChatOllama(...)` is constructed without a `num_predict` cap, so some live final answers are cut off mid-sentence before stating the recommended action in the expected phrasing — this caused 2 of 13 `test_member3.py` tests to fail only when Ollama is online (11/13 pass live); it is not a tool-calling defect.

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
execution is not evidence that a live model made tool calls. Live-mode evidence
(real `qwen2.5:3b` tool calls, the "Ollama Service: Online" indicator, an
expanded agent tab, and the tool-call inspector) is captured separately in
`screenshots/`; live recommendation wording can differ from the offline
fallback shown in this table.

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

## 6. Streamlit Dashboard & Integration

The interactive dashboard (`app.py`) is the project's single entry point, wiring all six agents behind one consistent operator workflow.

### Sidebar & Scenario Control
- The scenario selector reads keys directly from `data/scenarios.json`; the Ollama model selector offers `qwen2.5:3b`, `qwen3:4b`, `llama3.2`, and `qwen2.5:7b`.
- A live `is_ollama_reachable()` check renders an "Online" / "Offline (fallback)" badge so an operator always knows which inference path produced the LLM report.
- Switching the scenario or model clears the cached reports in `st.session_state` so results are never mislabeled as belonging to a different incident or model.

### Execution & Caching
- "Run All 6 AI Agents" invokes the five classical agents plus `LLMIncidentAgent(model_name=...).analyze(...)` once per click, caching all 6 `AgentReport`s and the LLM's `tools_used` trace in session state so later reruns (e.g. a feedback click) never re-invoke the LLM.

### Cross-Agent Comparison & Detailed Reports
- A pandas `DataFrame` renders Agent Architecture, Decision Mechanism, Likely Root Cause, Recommended Action, and Architectural Limitations side by side for all 6 agents.
- Per-agent tabs expand each report's Incident Summary, Evidence, Verification Steps, and Limitations straight from the shared 7-key `AgentReport` schema.

### LLM Tool Calling Inspector
- Displays the exact tool calls (`get_metrics`, `search_logs`, `get_deployment_history`, `check_previous_version`) returned by the LLM agent, with the caption explicitly noting when the offline fallback — not live inference — produced them.

### Learning Agent Feedback Simulator
- Lets an operator record one explicit success/failure for a scenario-eligible action (sourced from `LearningAgent.feedback_actions`); the callback updates only the Learning Agent's report and comparison row, persists the outcome to `data/experience.json`, and leaves the other 5 reports and the LLM untouched.

### Packaging & Verification
- `requirements.txt` is pinned to the exact validated versions (`streamlit==1.67.0`, `langchain==1.5.2`, `langchain-ollama==1.1.0`, `pydantic==2.14.4`, `pandas==3.1.1`).
- `tests/test_member4.py` verifies the pinning and package importability, confirms `screenshots/` has the expected coverage, and runs a 4-scenario `AppTest` smoke check of `app.py` itself.
- `screenshots/` captures the full operator workflow end to end: all 4 scenario overviews, an expanded agent tab, the tool-call inspector, and the feedback simulator before/after a recorded outcome — with live Ollama inference confirmed via the "Online" badge visible in several captures.

---

## 7. Setup & Execution Runbook

### Prerequisites
* Python 3.10+ (tested on Python 3.12.10 and 3.13)
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
python -m tests.test_member4

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
interactions without a browser. See [recorded results and package versions](results/member2_validation.json).

Member 4 validation, Python **3.12.10**, with `requirements.txt`
pinned and **Ollama installed locally with `qwen2.5:3b` running online**: **47
unittest tests discovered, 45 passed** (the 40 above plus the new 7-test
`tests.test_member4` packaging suite). The 2 failures are the pre-existing,
known `test_member3.py` live-answer-truncation issue described in Section 4,
reproducible only when Ollama is online; they are not a regression from pinning
or the new test file. The separate Member 1 script (10 checks) and the
six-agent script (24 checks, run live against Ollama) both passed. Browser
screenshots across all 4 scenarios, an agent tab, the tool inspector, and the
feedback simulator were captured live and are stored in `screenshots/`.

### Step 4a: Pinned Dependencies
`requirements.txt` is pinned to the exact versions validated above
(`streamlit==1.67.0`, `langchain==1.5.2`, `langchain-ollama==1.1.0`,
`pydantic==2.14.4`, `pandas==3.1.1`). Reinstall with `pip install -r requirements.txt`
after pulling to stay on the validated versions.

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

## 8. Submission Checklist Verification

- [x] **Five Classical Agents:** `simple_reflex.py`, `model_reflex.py`, `goal_based.py`, `utility_based.py`, `learning_agent.py` each correctly implement their intended decision paradigm.
- [x] **Offline six-agent integration:** All report schemas and the fallback tool path verified across the four shared scenarios.
- [x] **Live Ollama demonstration:** Verified by Member 4 — real model-driven tool calls (2-4 per scenario) and evidence-grounded reports confirmed across all 4 scenarios with `qwen2.5:3b` online. One known issue (final-answer truncation from a missing `num_predict` cap) is reported to Member 3 and does not affect tool-calling or schema compliance.
- [x] **Shared Scenario Telemetry:** All 6 agents receive identical scenario inputs from `data/scenarios.json`.
- [x] **Streamlit UI:** `app.py` allows selecting scenarios, running all 6 agents, viewing the side-by-side comparison table, and simulating learning feedback live.
- [x] **Learning Experience Persistence:** `data/experience.json` tracks outcome counts and adapts policy dynamically.
- [x] **Documentation & Deliverables:** Comprehensive `README.md`, pinned `requirements.txt`, individual member notes (`MEMBER1_NOTES.md`, `MEMBER2_NOTES.md`, `MEMBER3_NOTES.md`, `MEMBER4_NOTES.md`), and passing test suites.
- [x] **Screenshots:** Captured in `screenshots/` for all 4 scenarios, an expanded agent tab, the LLM tool inspector, and the feedback simulator before/after a recorded outcome.
- [ ] **Final packaging & submission:** Full test suite, pinned environment, and documentation are ready.

---

Screenshots and live-Ollama verification are now complete (Member 4). 
