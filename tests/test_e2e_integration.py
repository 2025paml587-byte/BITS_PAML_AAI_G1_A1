import json
from agents.simple_reflex import SimpleReflexAgent
from agents.model_reflex import ModelBasedReflexAgent
from agents.goal_based import GoalBasedAgent
from agents.utility_based import UtilityBasedAgent
from agents.learning_agent import LearningAgent
from agents.llm_agent import LLMIncidentAgent

REQUIRED_KEYS = {
    "agent_name",
    "incident_summary",
    "evidence",
    "likely_cause",
    "recommended_action",
    "verification_steps",
    "limitations",
}


def run_e2e():
    with open("data/scenarios.json", "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    for key, scenario in scenarios.items():
        print(f"\n=== End-to-End Integration Check: {key} ===")
        reports = [
            SimpleReflexAgent().analyze(scenario),
            ModelBasedReflexAgent().analyze(scenario),
            GoalBasedAgent().analyze(scenario),
            UtilityBasedAgent().analyze(scenario),
            LearningAgent().analyze(scenario, scenario_key=key),
        ]
        llm_report, tools_used = LLMIncidentAgent().analyze(key, scenario["title"])
        reports.append(llm_report)

        for r in reports:
            missing = REQUIRED_KEYS - set(r.keys())
            assert not missing, f"[{r.get('agent_name')}] Missing keys: {missing}"
            print(f"  [PASS] {r['agent_name']} -> {r['recommended_action'][:75]}")
        print(f"  [INFO] LLM tools invoked ({len(tools_used)}): {tools_used}")

    print("\nAll 6 agents passed end-to-end schema and execution checks across all 4 scenarios!")


if __name__ == "__main__":
    run_e2e()
