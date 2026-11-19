# Member 1 Daily Deliverable Log — Kiran
**Role:** Data Architect & Reflex Agents  
**Project:** Intelligent Production Incident Management System (Assignment 1 - Set 1)  

---

## Owned Files & Responsibilities
* `schema.py` — Shared `AgentReport` TypedDict contract and `format_report()` helper.
* `data/scenarios.json` — Standardized telemetry, logs, and deployment history for all 4 test scenarios (`Normal_Baseline`, `Scenario_A`, `Scenario_B`, `Scenario_C`).
* `agents/simple_reflex.py` — Stateless condition-action rule agent.
* `agents/model_reflex.py` — Stateful internal-baseline and deployment-delta agent.

---

## Daily Progress Tracker

### Day 1: Foundation & Shared Contracts — [COMPLETED]
* **Deliverables Completed:**
  * [x] Created GitHub repository with standard directory structure (`agents/`, `data/`, `tools/`).
  * [x] Implemented `schema.py` enforcing the 7 mandatory output keys (`agent_name`, `incident_summary`, `evidence`, `likely_cause`, `recommended_action`, `verification_steps`, `limitations`).
  * [x] Populated `data/scenarios.json` covering Normal, Critical, and Edge/Ambiguous scenarios (`Normal_Baseline`, `Scenario_A`, `Scenario_B`, `Scenario_C`).
  * [x] Pushed foundational commit to GitHub so Chetan (Member 2), Sourav (Member 3), and Member 4 can develop in parallel.
* **Verification:** Confirmed valid JSON parsing and schema imports across the team.

---

### Day 2: Core Reflex Agents — [COMPLETED]
* **Deliverables Completed:**
  * [x] Implemented `SimpleReflexAgent` in `agents/simple_reflex.py` using stateless threshold checks (`CRASH_LOOP`, DB connection saturation, `CPU > 85%`).
  * [x] Implemented `ModelBasedReflexAgent` in `agents/model_reflex.py` using an internal healthy baseline model (`CPU: 30%`, `RPS: 130`, `Latency: 50ms`, `DB: 25%`) and `deployment_history` correlation.
  * [x] Tested both agents across all 4 scenarios in `data/scenarios.json`.
* **Key Findings from Testing:**
  * On **Scenario C** (startup crash after config change), `SimpleReflexAgent` blindly recommends restarting the container, whereas `ModelBasedReflexAgent` detects the recent deployment change and recommends rolling back to `v2.1.0`.
  * On **Scenario B** (edge case: 92% CPU, 950 req/s, normal DB), `ModelBasedReflexAgent` calculates a `7.3x` traffic surge against its internal baseline while confirming DB health (`35%`).

---

### Day 3: Edge-Case Refinement & Schema Validation — [COMPLETED]
* **Deliverables Completed:**
  * [x] Hardened `agents/simple_reflex.py` with safe `.get()` lookups and added high-latency/error-rate threshold detection (`latency > 1000ms` or `error_rate > 5%`).
  * [x] Hardened `agents/model_reflex.py` against division-by-zero and added differentiation for crashes without recent deployments as well as runaway CPU processes (`high CPU` + `normal traffic`).
  * [x] Created and executed `tests/test_member1.py` verifying 100% compliance with the 7-key `AgentReport` schema across all 4 core scenarios plus a synthetic edge case.
  * **Verification:** All 10 test assertions (`2 agents x 5 scenarios`) passed with zero errors.
  * [X] Coordinate with Member 4 to verify smooth integration of both agents into `app.py`.

---

### Day 4: Comparison Table Narrative & End-to-End Integration — [COMPLETED]
* **Deliverables Completed:**
  * [x] Added the *"Analytical Comparison: Why Do Agent Decisions Differ?"* breakdown beneath the Cross-Agent Comparative Decision Matrix in `app.py`.
  * [x] Created `tests/test_e2e_integration.py` and verified all 6 agents (`SimpleReflex`, `ModelBasedReflex`, `GoalBased`, `UtilityBased`, `LearningAgent`, `LLMIncidentAgent`) across all 4 scenarios (`Normal_Baseline`, `Scenario_A`, `Scenario_B`, `Scenario_C`).
  * [x] Standardized `requirements.txt` with clean cross-platform top-level packages and verified live Streamlit dashboard execution on Python 3.13.
* **Verification:** All 4 scenarios ran end-to-end in the browser with zero errors.

---

### Day 5: Final QA, Rubric Audit & Documentation — [COMPLETED]
* **Deliverables Completed:**
  * [x] Audited all 6 agent implementations, `scenarios.json`, and `app.py` against every assignment rubric criterion.
  * [x] Contributed the Setup/Run guide and Comparative Evaluation table/narrative to `README.md`.
  * [x] Verified screenshot checklist and submission readiness with Anisha (Member 4), Chetan (Member 2), and Sourav (Member 3).
* **Status:** All Member 1 deliverables (Days 1–5) are complete and pushed to `main`.