# Member 4 Daily Deliverable Log — Anisha
**Role:** UI Lead, Integration & Packaging
**Project:** Intelligent Production Incident Management System (Assignment 1 - Set 1)
**Last Verified:** 20 November 2026

---

## Owned Files & Responsibilities
* `app.py` — Streamlit dashboard: scenario selector, telemetry overview, 6 agent cards/tabs, cross-agent comparison table, LLM tool-call inspector, learning-feedback simulator.
* `requirements.txt` — Project dependencies, pinned to exact validated versions.
* `screenshots/` — Captured UI evidence for all 4 scenarios, an expanded agent tab, the LLM tool inspector, and the feedback simulator.
* `tests/test_member4.py` — Packaging/readiness suite: pinned-dependency and import checks, screenshot-coverage checks, and a 4-scenario Streamlit `AppTest` smoke test.
* **Shared responsibilities:** `README.md` (setup/run guide, architecture overview, comparative evaluation — shared narrative content with Members 1 & 2), end-to-end integration across all 6 agents, and live-Ollama verification (shared with Member 3).

---

## Architectural & Technical Design

### 1. Streamlit Dashboard Layout (`app.py`)
- **Sidebar:** scenario selector (`data/scenarios.json` keys), Ollama model selector (`qwen2.5:3b`, `qwen3:4b`, `llama3.2`, `qwen2.5:7b`), a live `is_ollama_reachable()` status indicator, and an agent-taxonomy legend.
- **Telemetry overview:** a 6-metric card row (CPU, P95 latency, error rate, request rate, DB pool, current version) plus a raw logs/deployment-history/previous-version expander sourced directly from the shared scenario JSON.
- **Execution:** the "Run All 6 AI Agents" button invokes the five classical agents and `LLMIncidentAgent(model_name=...).analyze(...)`, caching all 6 reports plus `tools_used` in `st.session_state` so Streamlit reruns (e.g. a feedback click) never re-invoke the LLM.
- **State invalidation:** switching the scenario or model clears `last_reports`/`tools_used` so stale reports are never mislabeled as belonging to a different incident or model.

### 2. Cross-Agent Comparison & Detailed Reports
- Builds a pandas `DataFrame` mapping each `AgentReport` to (Agent Architecture, Decision Mechanism, Likely Root Cause, Recommended Action, Architectural Limitations), rendered with `st.dataframe`.
- Per-agent expandable tabs render Incident Summary, Likely Root Cause, Recommended Action, Verification Steps, Evidence, and Limitations from the shared 7-key `AgentReport` schema.

### 3. LLM Tool Calling Inspector
- Renders the `tools_used` list returned by `LLMIncidentAgent.analyze()` as individual tool-call traces, and the caption explicitly notes that offline-fallback runs execute the same tools without live model inference.

### 4. Learning Agent Feedback Simulator
- `record_learning_feedback()` is a button `on_click` callback that calls `LearningAgent.record_outcome(scenario_key, action_key, success, scenario=scenario)`, re-analyzes only the Learning Agent, and splices the refreshed report back into `last_reports` (the other 5 reports and the LLM are not re-invoked).
- `LearningAgent.feedback_actions(scenario)` supplies the eligible-action dropdown so the UI can never submit feedback for an action that isn't valid for the active scenario.

### 5. Dependency Pinning (`requirements.txt`)
- Pinned to the exact versions validated in this environment (Python 3.12.10): `streamlit==1.67.0`, `langchain==1.5.2`, `langchain-ollama==1.1.0`, `pydantic==2.14.4`, `pandas==3.1.1`.

### 6. Live Ollama Integration
- Use Ollama locally (`winget install --id Ollama.Ollama -e`, v0.40.16) and pulled `qwen2.5:3b` (confirmed `tools` capability via `/api/tags`).
- Verified real model-driven tool calls (2-4 distinct tools per scenario, not the offline fallback) across all 4 scenarios.

### 7. `tests/test_member4.py`
- `Member4RequirementsTests` — every line in `requirements.txt` is exactly pinned, and every pinned package imports successfully.
- `Member4ScreenshotsTests` — `screenshots/` isn't just the placeholder package, every scenario has at least one screenshot, and the agent-tab/tool-inspector/feedback-simulator captures all exist.
- `Member4AppSmokeTests` — a minimal `app.py` `AppTest` smoke run (offline Ollama, isolated temp history) across all 4 scenario keys, asserting no exceptions and 6 reports produced per scenario.

---

## Known Issues & Limitations
- **LLM answer truncation (Member 3-owned, reported not fixed):** `ChatOllama(...)` in `agents/llm_agent.py` is constructed without a `num_predict` (max output tokens) parameter. Some live final answers are cut off mid-sentence before stating the recommended action, causing 2 of `test_member3.py`'s 13 tests to fail only when Ollama is online (11/13 pass live); tool selection and root-cause reasoning are unaffected.
- `screenshots/__init__.py` remains alongside the captured images; it predates this work and was left untouched.
- Local Ollama (`qwen2.5:3b`) inference latency is 5-20s per agent run; context window and tool-calling precision are subject to the model's small parameter scale, as surfaced in each LLM agent report's own limitations field.

---

## Daily Progress Tracker

### Day 1: Foundation — [COMPLETED]
* [x] Reviewed `schema.py` and `data/scenarios.json` delivered by Member 1.
* [x] Created skeleton `app.py` and initial `requirements.txt`.

### Day 2: Core UI Layout — [COMPLETED]
* [x] Built the Streamlit layout: sidebar scenario picker, Ollama model selector, "Run All 6 Agents" button, per-agent output tabs.
* [x] Added telemetry overview cards (CPU, latency, error rate, RPS, DB pool, current version) and raw logs/deployment-history/previous-version accordions.

### Day 3: Classical Agent Integration — [COMPLETED]
* [x] Integrated all 5 classical agents (`SimpleReflexAgent`, `ModelBasedReflexAgent`, `GoalBasedAgent`, `UtilityBasedAgent`, `LearningAgent`) into `app.py` and verified UI rendering across all 4 scenarios.

### Day 4: Full Assembly — [COMPLETED]
* [x] Wired `LLMIncidentAgent` into `app.py` with `st.spinner`, an Ollama online/offline indicator, and a tool-call trace inspector.
* [x] Built the side-by-side Cross-Agent Comparative Decision Matrix and the "Why Do Agent Decisions Differ?" narrative panel.
* [x] Added the Learning Agent Feedback Simulator (scenario-specific eligible actions, immediate report/comparison refresh, state reset on scenario/model change).
* [x] Confirmed end-to-end execution across all 4 scenarios with zero UI errors.

### Day 5: QA, Live Verification & Packaging — [COMPLETED]
* [x] Pinned `requirements.txt` to the exact versions validated in this environment and re-ran the full suite to confirm no regressions.
* [x] Used Ollama and `qwen2.5:3b` locally; verified live model-driven tool calls and 24/24 six-agent schema checks online.
* [x] Captured 8 screenshots in `screenshots/`: all 4 scenario overviews, an expanded LLM agent tab, the tool-calling inspector, and the feedback simulator before/after a recorded outcome.
* [x] Added `tests/test_member4.py` (7 tests: pinned-dependency checks, screenshot coverage, 4-scenario app smoke test).
* [x] Reconciled `README.md`: ownership/status note, directory tree, LLM verification note, test counts, pinned-dependency note, and submission checklist.
* **Status:** Member 4's implementation, testing, and documentation work is complete. Final packaging and submission sign-off require full-team coordination and are not certified by this log alone.

---

## Validation Commands & Evidence

```bash
python -m unittest discover -s tests -v
python -m tests.test_member1
python -m tests.test_e2e_integration
python -m tests.test_member4
```

On **20 November 2026**, Python **3.12.10**, with `requirements.txt` pinned and **Ollama online with `qwen2.5:3b`**: **47 unittest tests discovered, 45 passed** (the original 40 plus the new 7-test `tests.test_member4` suite). The 2 failures are the known `test_member3.py` live-answer-truncation issue described above, reproducible only when Ollama is online; they are not a regression from pinning or the new test file. The separate Member 1 script (10 checks) and the six-agent script (24 checks, run live against Ollama) both passed.

* [Captured screenshots](screenshots/)
* [Project README: agent mechanisms, comparison results, and setup/run guide](README.md)
