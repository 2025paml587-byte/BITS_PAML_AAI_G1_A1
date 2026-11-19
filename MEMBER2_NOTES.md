# Member 2 Daily Deliverable Log — Chetan

**Role:** Goal, Utility & Learning Agents

**Project:** Intelligent Production Incident Management System (Assignment 1 - Set 1)

**Last Verified:** 19 November 2026

---

## Owned Files & Responsibilities

* `agents/goal_based.py` — Candidate recovery plans and evaluation against target SLA goals.
* `agents/utility_based.py` — Weighted recovery scoring across speed, safety, and cost.
* `agents/learning_agent.py` — Action selection using persistent success/failure counts and explicit outcome feedback.
* `data/experience.json` — Synthetic initial experience history and persistent outcome counts.
* `tests/test_member2_agents.py`, `tests/test_member2_ui.py`, and `tests/member2_fixtures.py` — Agent and UI integration tests using isolated history fixtures.
* `results/member2_validation.json` — Recorded test results, scenario reports, and before/after learning evidence.
* **Shared responsibilities:** Member 2's comparison narrative and learning-feedback integration in `app.py`, plus comparative analysis and verification documentation in `README.md`.

---

## Daily Progress Tracker

### Day 1: Foundation & Shared Contracts — [COMPLETED]

* **Deliverables Completed:**
  * [x] Reviewed Member 2's assigned scope and the repository structure established by Member 1.
  * [x] Reviewed `schema.py` and its seven-field `AgentReport` contract.
  * [x] Reviewed all four shared scenarios: `Normal_Baseline`, `Scenario_A`, `Scenario_B`, and `Scenario_C`.
  * [x] Aligned agent interfaces with `analyze(scenario)` and the Learning Agent's optional `scenario_key` argument.
* **Verification:** Confirmed the existing shared schema and scenarios could be used without modifying Member 1's deliverables. Day 1 did not assign a separate agent implementation to Member 2.

---

### Day 2: Goal-Based & Utility-Based Agents — [COMPLETED]

* **Deliverables Completed:**
  * [x] Implemented `GoalBasedAgent` to evaluate candidate recovery states against all three goals: `service_status=RUNNING`, `error_rate_percent < 1%`, and `latency_ms < 200`.
  * [x] Implemented `UtilityBasedAgent` with the explicit formula `U = 0.5 × Speed + 0.3 × Safety − 0.2 × Cost` and configurable weights.
  * [x] Selected the first goal-achieving plan for the Goal-Based Agent and the highest-utility eligible plan for the Utility-Based Agent.
  * [x] Added evidence, verification steps, and limitations to every report using the shared schema.
  * [x] Tested normal operation, DB exhaustion, traffic surge, and startup failure, including both `DOWN` and `CRASH_LOOP`.
* **Key Findings from Testing:**
  * On **Scenario B**, the goal agent selects scaling alone. The utility agent selects scaling plus caching (**57.00**) over scaling alone (**55.50**) because of its assumed cost advantage.
  * Selected utility scores are **80.00** for Normal_Baseline, **65.50** for Scenario_A, **57.00** for Scenario_B, and **69.00** for Scenario_C.
  * Rollback candidates require a reported change and a previous version marked `HEALTHY`; unsupported SLA violations escalate for diagnosis.
* **Verification:** All four scenarios produce valid seven-field reports. Recovery projections and utility ratings are documented as teaching assumptions; the agents recommend actions without executing them.

---

### Day 3: Learning Agent & Persistent Experience — [COMPLETED]

* **Deliverables Completed:**
  * [x] Implemented `LearningAgent` and the synthetic initial history in `data/experience.json`.
  * [x] Ranked eligible actions using `(success + 1) / (success + failure + 2)` with deterministic tie-breaking and cold-start behavior.
  * [x] Implemented `record_outcome()` to persist an explicitly supplied success or failure. Analysis alone never records a successful recovery.
  * [x] Added atomic JSON replacement, validation of stored counts, rejection of corrupt history, and a default path independent of the working directory.
  * [x] Verified that recorded failures change recommendations and that the change survives reloading the history file.
* **Key Findings from Testing:**
  * With the shipped **Scenario B** history, scaling alone has estimate **6/7**, compared with **3/5** for scaling plus caching.
  * Five explicit scale-out failures reduce its estimate to **6/12**, causing the learning agent to prefer scaling plus caching.
* **Verification:** Persistent feedback and changed decisions were demonstrated with temporary history files. The original delivery passed **17 agent tests**; the expanded suite now passes **20**. The project's stored experience counts were preserved during validation.

---

### Day 4: Comparison Table Narrative & End-to-End Integration — [COMPLETED]

* **Deliverables Completed:**
  * [x] Corrected the shared comparison narrative to explain goal satisfaction, calculated utility, explicit learning feedback, and agent limitations.
  * [x] Replaced the UI's unsupported feedback action names with scenario-specific options from `LearningAgent.feedback_actions(scenario)`.
  * [x] Added optional scenario validation to `record_outcome()` so the UI cannot record an inapplicable action.
  * [x] Made feedback immediately refresh the learning report, evidence, history display, and comparison row while retaining the other agents' reports.
  * [x] Cleared outdated reports when the selected scenario or model changes.
  * [x] Added **7 Streamlit UI integration tests** covering all four scenarios, feedback persistence, changed recommendations, scenario/model switching, unavailable actions, and corrupt-history feedback.
  * [x] Ran the existing six-agent integration script across all four shared scenarios.
* **Verification:** All **7 UI tests** and **24 six-agent report checks** passed. Ordinary reruns do not duplicate feedback. Streamlit AppTest exercised the real application with Ollama availability forced offline and the real fallback tools executed; this was not a live-model or browser screenshot test.

---

### Day 5: Final QA, Rubric Audit & Documentation — [COMPLETED]

* **Deliverables Completed:**
  * [x] Reviewed Member 2's work against the assignment requirements for correct decision mechanisms, shared inputs, persistent learning, comparison reasoning, and limitations.
  * [x] Corrected stale utility scores and removed duplicate, inconsistent comparison tables from `README.md`.
  * [x] Corrected claims that analysis automatically increments learning counts or that the Learning Agent implements an exploration/problem-generator mechanism.
  * [x] Documented model assumptions, synthetic seed history, cold starts, small-sample limitations, and the single-writer JSON persistence constraint.
  * [x] Recorded the complete validation results and the before/after learning demonstration in `results/member2_validation.json`.
  * [x] Updated Member 2's progress log, integration guidance, demo instructions, and validation scope.
* **Verification:** On **19 November 2026**, using Python **3.12.3**, all **40 discovered tests** passed: **20 Member 2 agent tests + 7 Member 2 UI tests + 13 Member 3 tests**. The separate Member 1 script passed **10 agent/scenario checks**, and the six-agent script passed **24 report checks**. Member 1/3 implementations, shared schema/scenarios, dependency declarations, and project experience counts were unchanged by Member 2's integration work.
* **Status:** Member 2's implementation, shared integration, and documentation work is complete within the recorded offline validation scope. Live Ollama verification, browser demo screenshots, and final packaging remain with Members 3/4. This log does not certify those tasks or a GitHub push.

---

## Validation Commands & Evidence

Run from the project directory after installing the repository's dependencies:

```bash
python -m unittest tests.test_member2_agents tests.test_member2_ui -v
python -m unittest discover -s tests -v
python -m tests.test_member1
python -m tests.test_e2e_integration
```

The last two scripts are separate checks and are not executed by unittest discovery. Member 2's feedback tests use fixed synthetic fixtures and temporary files. UI tests always use the offline fallback; other tests may use a live Ollama model when available.

* [Recorded validation results and package versions](results/member2_validation.json)
* [Project README: agent mechanisms, comparison results, and learning demo](README.md)
