"""Member 2: explicit weighted utility over applicable recovery candidates."""

import math

from schema import AgentReport, format_report
from agents.goal_based import VERIFICATION, meets_sla, recovery_options, telemetry_evidence


class UtilityBasedAgent:
    def __init__(self, speed_weight=0.5, safety_weight=0.3, cost_weight=0.2):
        self.name = "Utility-Based Agent"
        weights = (speed_weight, safety_weight, cost_weight)
        if any(not math.isfinite(w) or w < 0 for w in weights) or not math.isclose(sum(weights), 1.0):
            raise ValueError("Utility weights must be finite, nonnegative and sum to 1.")
        self.weights = weights

    def analyze(self, scenario: dict) -> AgentReport:
        cause, plans = recovery_options(scenario)
        speed_w, safety_w, cost_w = self.weights
        evidence = telemetry_evidence(scenario)
        evidence.append(
            f"Utility = {speed_w:g} * Speed + {safety_w:g} * Safety - {cost_w:g} * Cost. "
            "Ratings are illustrative 0..100 values, not observed probabilities."
        )
        evidence.append("Only candidates predicted to meet all SLA goals are eligible; predictions are simulation assumptions.")
        eligible = []
        for plan in plans:
            score = speed_w * plan.speed + safety_w * plan.safety - cost_w * plan.cost
            feasible = plan.projected_state is not None and meets_sla(plan.projected_state)
            evidence.append(
                f"Candidate {plan.key}: Speed={plan.speed:g}, Safety={plan.safety:g}, Cost={plan.cost:g}; "
                f"utility={score:.2f}; projected={plan.projected_state}; eligible={feasible}."
            )
            if feasible:
                eligible.append((score, plan))
        if eligible:
            score, selected = max(eligible, key=lambda item: item[0])
            action = selected.action
            evidence.append(f"Selected {selected.key} with maximum eligible utility={score:.2f}; ties use declared order.")
        else:
            action = "Escalate to SRE for diagnosis; no eligible recovery candidate."
        return format_report(
            self.name, f"Weighted recovery utility for {scenario['title']}.", evidence,
            cause, action, list(VERIFICATION),
            "Static subjective ratings and hand-authored recovery predictions; scores are not success percentages. "
            "Caching assumes cacheable requests and scaling assumes available capacity. Weights do not learn from outcomes.",
        )
