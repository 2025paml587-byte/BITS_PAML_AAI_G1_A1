# Member 2 deliverables

Implemented `agents/goal_based.py`, `agents/utility_based.py`,
`agents/learning_agent.py`, and `data/experience.json`. The accompanying tests
cover these modules only. All existing files are unchanged, including Member 1's
schema/scenarios/reflex agents and the UI, dependencies, and project README.

## Decision mechanisms

- **Goal-Based Agent:** enumerates applicable plans, evaluates each projected
  state against `RUNNING`, errors `< 1%`, and latency `< 200ms`, and selects the
  first plan satisfying all three conditions. This is a single-step planning
  model; it does not rank feasible plans by cost or risk.
- **Utility-Based Agent:** scores candidates using
  `U = 0.5 * Speed + 0.3 * Safety - 0.2 * Cost`, then chooses the highest-scoring
  candidate predicted to satisfy the SLA. Ratings are on a 0–100 scale; utility
  is not a success percentage. Weights can be supplied to the constructor and
  must be nonnegative and sum to one.
- **Learning Agent:** ranks eligible actions by the smoothed historical success
  estimate `(success + 1) / (success + failure + 2)`. Equal estimates use candidate
  order. Unseen cases start with equal priors and the first goal-achieving plan.
  Recording success/failure updates persistent counts and can change later choices.

Candidate definitions live in `goal_based.py` and are shared by the three agents.
Recovery predictions and speed/safety/cost ratings are explicit teaching
assumptions, not measurements or recovery guarantees. Scaling assumes available
capacity; caching assumes cacheable requests. A traffic threshold of three times
130 requests/second is a static baseline assumption. Unsupported SLA violations
escalate for diagnosis. Rollback requires a reported change and a previous version
marked `HEALTHY`. No recovery operations are executed.

## Integration interface for Member 4

All agents return the existing seven-key `AgentReport` via `schema.format_report`.
No new packages are needed. The following calls are ready for UI integration:

```python
from agents.goal_based import GoalBasedAgent
from agents.utility_based import UtilityBasedAgent
from agents.learning_agent import LearningAgent

goal_report = GoalBasedAgent().analyze(scenario)
utility_report = UtilityBasedAgent().analyze(scenario)
learning_agent = LearningAgent()
learning_report = learning_agent.analyze(scenario, scenario_key=selected_key)
```

Pass the selected scenario key explicitly when available. The optional-key form
`analyze(scenario)` matches the supplied shared scenarios by content; other input
gets a deterministic separate key rather than silently using `Scenario_A`.

The learning report lists stable action keys in its evidence. After evaluating
the chosen action, record **one** explicit outcome, for example:

```python
# Only after an observed or explicitly simulated failed scale-out attempt:
learning_agent.record_outcome("Scenario_B", "scale_out", success=False)
```

Use `success=True` for a verified successful outcome. Calling `analyze()` alone
does not update counts: generating a recommendation is not evidence of success.
The supplied history is synthetic demonstration data. With the shipped Scenario B
counts, `scale_out` has estimate `6/7`, versus `3/5` for `scale_and_cache`. Five
recorded scale-out failures reduce its estimate to `6/12`, so the next analysis
chooses `scale_and_cache`. Tests demonstrate this using temporary history files.

The default history path is relative to the project, independent of the working
directory. `LearningAgent(exp_path=...)` supports isolated experiments. Missing
files start with empty history; corrupt files are rejected without overwriting.
Writes use atomic replacement, but this local JSON implementation assumes one
writer and does not deduplicate repeated feedback submissions.

## Scenario results and comparison

| Shared scenario | Goal-Based | Utility-Based | Learning (shipped history) |
| --- | --- | --- | --- |
| Normal_Baseline | Monitor | Monitor | Monitor |
| Scenario_A | Roll back patch and drain DB connections | Same plan | Same plan: estimate 5/6 |
| Scenario_B | Scale replicas | Scale replicas plus caching | Scale replicas: estimate 6/7 |
| Scenario_C (`DOWN`) | Roll back config/release to v2.1.0 | Same plan | Same plan: estimate 7/8 |

Scenario B exposes the different decision mechanisms: the goal agent accepts
the first feasible plan; utility prefers scaling plus caching (57.00) over scaling
alone (55.50), using the assumed cost advantage; learning prefers scaling alone
because its recorded outcomes are stronger. The learning preference reverses
after sufficient explicit failures. Every report includes evidence, verification
steps, and limitations for the UI's eventual comparison view.

## Validation

From the project directory:

```bash
python -m unittest discover -s tests -p 'test_member2_agents.py' -v
```

Result on 14 November 2026 with Python 3.12.3: **17 tests passed**. Coverage includes
all four existing scenarios, exact report schema, input preservation, strict SLA
boundaries, both `DOWN` and `CRASH_LOOP`, unhealthy rollback targets, unsupported
bottlenecks, zero DB capacity, actual utility calculations and weight sensitivity,
persistent success/failure updates, changed decisions after reloading, cold starts,
scenario isolation, working-directory independence, corrupt history, and invalid
feedback. Tests preserve the shipped experience counts.

The Streamlit app and LLM integration are outside this delivery and have not been
implemented or tested here.
