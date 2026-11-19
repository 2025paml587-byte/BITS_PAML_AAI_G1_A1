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

### Day 4: Comparison Table & Analytical Write-Up — [UPCOMING]
* **Planned Deliverables:**
  * [ ] Partner with Chetan (Member 2) to implement the side-by-side Comparison Table logic in `app.py`.
  * [ ] Draft the technical explanation contrasting stateless reflex rules against internal-model state tracking and higher-level deliberative/learning/LLM agents.
  * [ ] Participate in end-to-end testing across all 4 scenarios in Streamlit.

---

### Day 5: Final QA & Rubric Review — [UPCOMING]
* **Planned Deliverables:**
  * [ ] Audit all agent outputs against the assignment rubric (verifying limitations, evidence lists, and verification steps are clear).
  * [ ] Review final screenshots and `README.md` with the team prior to submission.
