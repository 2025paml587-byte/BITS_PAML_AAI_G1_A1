import json
from agents.simple_reflex import SimpleReflexAgent
from agents.model_reflex import ModelBasedReflexAgent

REQUIRED_KEYS = {
    "agent_name",
    "incident_summary",
    "evidence",
    "likely_cause",
    "recommended_action",
    "verification_steps",
    "limitations",
}


def validate_report(report: dict, agent_label: str, scenario_name: str):
    missing = REQUIRED_KEYS - set(report.keys())
    assert not missing, f"[{agent_label} | {scenario_name}] Missing keys: {missing}"
    assert isinstance(report["evidence"], list) and len(report["evidence"]) > 0, "Evidence must be a non-empty list"
    assert isinstance(report["verification_steps"], list) and len(report["verification_steps"]) > 0, "Verification steps must be a non-empty list"
    for k in REQUIRED_KEYS:
        assert report[k], f"[{agent_label} | {scenario_name}] Empty value for key: {k}"


def run_tests():
    with open("data/scenarios.json", "r") as f:
        scenarios = json.load(f)

    # Synthetic edge case: high CPU without traffic spike (runaway process)
    scenarios["Synthetic_CPU_Bug"] = {
        "title": "Synthetic Edge: High CPU Without Traffic Spike",
        "category": "Edge",
        "metrics": {
            "service_status": "DEGRADED",
            "cpu_percent": 95,
            "latency_ms": 900,
            "error_rate_percent": 2.0,
            "requests_per_sec": 140,
            "db_active_connections": 20,
            "db_max_connections": 100,
        },
        "deployment_history": {"last_change": "None"},
        "previous_version": {"version": "v2.1.0", "status": "HEALTHY"},
    }

    agents = [SimpleReflexAgent(), ModelBasedReflexAgent()]

    for s_key, s_data in scenarios.items():
        print(f"\n=== Testing Scenario: {s_key} ===")
        for agent in agents:
            report = agent.analyze(s_data)
            validate_report(report, agent.name, s_key)
            print(f"  [PASS] {agent.name} -> Action: {report['recommended_action']}")

    print("\nAll Member 1 schema and edge-case tests passed successfully!")


if __name__ == "__main__":
    run_tests()
