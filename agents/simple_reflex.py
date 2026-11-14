from schema import format_report, AgentReport


class SimpleReflexAgent:
    def __init__(self):
        self.name = "Simple Reflex Agent"

    def analyze(self, scenario: dict) -> AgentReport:
        m = scenario["metrics"]

        # Pure condition-action rules based strictly on immediate metrics
        if m["service_status"] in ("CRASH_LOOP", "DOWN"):
            cause = "Service process is down or crashing."
            action = "Restart service container immediately."
            evidence = [f"service_status={m['service_status']}"]
        elif m["db_active_connections"] >= m["db_max_connections"]:
            cause = "Database connection pool is exhausted."
            action = "Flush idle DB connections and increase max pool limit."
            evidence = [
                f"DB connections: {m['db_active_connections']}/{m['db_max_connections']}",
                f"API latency: {m['latency_ms']}ms",
            ]
        elif m["cpu_percent"] > 85:
            cause = "High CPU utilization detected."
            action = "Scale out service replicas."
            evidence = [
                f"CPU usage: {m['cpu_percent']}%",
                f"Latency: {m['latency_ms']}ms",
            ]
        else:
            cause = "All immediate metrics are within normal thresholds."
            action = "No action required; continue standard monitoring."
            evidence = [
                f"Status={m['service_status']}",
                f"CPU={m['cpu_percent']}%",
                f"Latency={m['latency_ms']}ms",
            ]

        return format_report(
            agent_name=self.name,
            summary=f"Evaluated {scenario['title']} using stateless threshold rules.",
            evidence=evidence,
            cause=cause,
            action=action,
            verification=[
                "Verify /health endpoint returns HTTP 200 OK",
                "Confirm error_rate_percent drops below 1%",
            ],
            limitations="Stateless: ignores deployment history, logs, and past incident outcomes.",
        )
