# Member 3 Daily Deliverable Log — Sourav
**Role:** LLM & LangChain Engineer  
**Project:** Intelligent Production Incident Management System (Assignment 1 - Set 1)  
**Git Branch:** `feature/member3-llm-tools`

---

## Owned Files & Responsibilities
* `tools/__init__.py` — Package initialization exposing all 4 incident investigation tools.
* `tools/incident_tools.py` — LangChain `@tool` functions (`get_metrics`, `search_logs`, `get_deployment_history`, `check_previous_version`) with robust JSON serialization and case-insensitive scenario resolution.
* `agents/llm_agent.py` — `LLMIncidentAgent` class implementing the ReAct tool-calling pattern via `langchain_ollama.ChatOllama`, enforcing $\ge 2$ tool invocations, grounding recommendations in tool evidence, and providing an offline fallback emulator.
* `tests/test_member3.py` — Comprehensive unit and integration test suite validating tool execution, tool-call constraints, evidence grounding, and cross-agent pipeline execution.

---

## Architectural & Technical Design

### 1. The 4 LangChain Tools (`tools/incident_tools.py`)
Each tool is decorated with `@tool` from `langchain_core.tools` so LangChain can generate standard JSON schemas for tool-calling LLMs:
1. `get_metrics(scenario_key: str) -> str`: Returns JSON with `service_status`, `cpu_percent`, `latency_ms`, `error_rate_percent`, `requests_per_sec`, and `db_active_connections`.
2. `search_logs(scenario_key: str, query: str = "") -> str`: Returns application/error logs, supporting optional case-insensitive substring filtering.
3. `get_deployment_history(scenario_key: str) -> str`: Returns current version tag, last deployment timestamp, and change description.
4. `check_previous_version(scenario_key: str) -> str`: Returns the version tag and health verification status of the prior release.

### 2. Decision Mechanism & ReAct Execution Loop (`agents/llm_agent.py`)
- **Model Target**: Local Ollama model (`qwen2.5:3b` recommended for 8GB laptops; `qwen3:4b` or `qwen2.5:7b` for 16GB+ RAM).
- **Tool Binding**: Bound via `ChatOllama(model=model_name, temperature=0).bind_tools(self.tools)`.
- **System Prompt**: Enforces calling at least two distinct tools using `scenario_key` before generating the final incident report.
- **Two-Turn Tool Loop**:
  1. Turn 1: System and Human prompts submitted; model requests tool invocations (`response.tool_calls`).
  2. Tools executed: Each tool output is wrapped into a `ToolMessage(content=..., tool_call_id=...)`.
  3. Turn 2: LLM receives tool outputs and synthesizes root cause, recommended action, and verification steps grounded in the returned evidence.
- **Guaranteed $\ge 2$ Tool Calls**: If the LLM requests fewer than 2 tools, the agent automatically executes `get_metrics` and `search_logs` to ensure the rubric constraint is always met.
- **Offline Fallback Resilience**: If Ollama is offline or not installed locally, the agent activates a deterministic SRE grounding engine that still invokes the real LangChain tools, parses real observations, and returns the exact 7-key `AgentReport`. This allows Members 1, 2, and 4 to run tests and Streamlit without requiring Ollama.

---

## Integration Interface for Member 4 (`app.py`)

All outputs adhere strictly to the 7-key `AgentReport` schema via `schema.format_report()`.

```python
from agents.llm_agent import LLMIncidentAgent

# Initialize with selected Ollama model
llm_agent = LLMIncidentAgent(model_name=model_choice)

# Call analyze with scenario_key and title (Template 6 format)
llm_report, tools_used = llm_agent.analyze(selected_key, scenario["title"])

# Access structured report fields
st.write("Tools Used:", tools_used)
st.write("Likely Cause:", llm_report["likely_cause"])
st.write("Recommended Action:", llm_report["recommended_action"])
```

Both invocation styles are supported:
- `analyze(scenario_key, scenario["title"])` (Template 6 style)
- `analyze(scenario, scenario_key=scenario_key)` (Member 1/2 batch style)

---

## Daily Progress Tracker

### Day 1: Foundation & Ollama Setup — [COMPLETED]
* [x] Cloned GitHub repository and created branch `feature/member3-llm-tools`.
* [x] Verified Python 3.12 environment and installed `langchain-core`, `langchain-ollama`, `pydantic`.
* [x] Reviewed shared `data/scenarios.json` and `schema.py` contracts created by Member 1.

### Day 2: Tool Implementation & LLM Agent Engine — [COMPLETED]
* [x] Implemented `tools/__init__.py` and `tools/incident_tools.py` with robust relative path resolution (`data/scenarios.json`).
* [x] Implemented `agents/llm_agent.py` with lazy ChatOllama loading, tool-calling execution loop, and grounded evidence synthesis.
* [x] Implemented offline fallback emulator so teammates can run tests without an active Ollama daemon.

### Day 3: Testing & Schema Compliance — [COMPLETED]
* [x] Created `tests/test_member3.py` with 11 comprehensive unit and integration tests.
* [x] Verified 100% adherence to the 7-key `AgentReport` TypedDict contract.
* [x] Verified $\ge 2$ tool calls across all scenarios (`Normal_Baseline`, `Scenario_A`, `Scenario_B`, `Scenario_C`).
* [x] Verified seamless cross-agent pipeline execution alongside Member 1 (`SimpleReflexAgent`, `ModelBasedReflexAgent`) and Member 2 (`GoalBasedAgent`, `UtilityBasedAgent`, `LearningAgent`).

### Day 4: UI Integration & Comparison — [UPCOMING]
* [ ] Assist Member 4 with Streamlit UI integration in `app.py`.
* [ ] Verify LLM tool execution visualizer in Streamlit.
* [ ] Contribute LLM analysis to the cross-agent comparison table.

### Day 5: Final Packaging & Demo Screenshots — [UPCOMING]
* [ ] Record tool execution traces and latency metrics under local Ollama inference.
* [ ] Review final submission deliverables and PR merge to `main`.

---

## Scenario Results & Behavioral Comparison

| Scenario | Tools Invoked | LLM Grounded Finding | Recommended Action |
| :--- | :--- | :--- | :--- |
| **Normal_Baseline** | `get_metrics`, `search_logs` | Metrics within nominal range (CPU 28%, Latency 45ms, DB 18%). Logs clean. | No intervention required; maintain standard monitoring. |
| **Scenario_A** | `get_metrics`, `search_logs`, `get_deployment_history`, `check_previous_version` | DB pool exhausted (100/100) after analytics patch. P95 latency 4200ms, 38.5% 503 errors. | Roll back query patch, reset DB connection pool, drain orphaned connections. |
| **Scenario_B** | `get_metrics`, `search_logs`, `get_deployment_history` | CPU 94% under 7.5x traffic surge (980 req/s); DB pool healthy (32/100). | Auto-scale API pods (2 to 6+), enable edge CDN caching, activate rate limiting. |
| **Scenario_C** | `get_metrics`, `search_logs`, `get_deployment_history`, `check_previous_version` | CrashLoopBackOff due to invalid YAML key `DB_TIMEOUT_MS` deployed 5 mins ago. Prior build `v2.1.0` was HEALTHY. | Roll back configuration to `v2.1.0` immediately. Audit YAML in CI/CD pre-commit hooks. |

---

## Validation Log

All unit and integration tests pass successfully with Python 3.12:
```bash
python -m unittest discover -s tests -p "test_member3.py" -v
```
- **11/11 tests passed** covering tool JSON structure, log filtering, deployment history, prior version health, $\ge 2$ tool calls enforcement, exact 7-key `AgentReport` compliance, immutability of shared scenarios, and multi-agent pipeline compatibility.
