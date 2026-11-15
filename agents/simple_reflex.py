from schema import format_report, AgentReport


class SimpleReflexAgent:
    def __init__(self):
        self.name = "Simple Reflex Agent"

    def analyze(self, scenario: dict) -> AgentReport:
        m = scenario.get("metrics", {})
        status = m.get("service_status", "UNKNOWN")
        cpu = m.get("cpu_percent", 0)
        latency = m.get("latency_ms", 0)
        error_rate = m.get("error_rate_percent", 0.0)
        db_active = m.get("db_active_connections", 0)
        db_max = max(1, m.get("db_max_connections", 100))

        # Pure condition-action rules based strictly on immediate metrics
        if status in ("CRASH_LOOP", "DOWN"):
            cause = "Service process is down or in a crash loop."
            action = "Restart service container immediately."
            evidence = [f"service_status={status}"]
        elif db_active >= db_max:
            cause = "Database connection pool is exhausted."
            action = "Flush idle DB connections and increase max pool limit."
            evidence = [
                f"DB connections: {db_active}/{db_max}",
                f"API latency: {latency}ms",
            ]
        elif cpu > 85:
            cause = "High CPU utilization detected."
            action = "Scale out service replicas."
            evidence = [
                f"CPU usage: {cpu}%",
                f"Latency: {latency}ms",
            ]
        elif latency > 1000 or error_rate > 5.0:
            cause = "Elevated API latency or error rate without CPU/DB saturation."
            action = "Restart worker processes and check upstream timeouts."
            evidence = [
                f"Latency: {latency}ms",
                f"Error rate: {error_rate}%",
            ]
        else:
            cause = "All immediate metrics are within normal thresholds."
            action = "No action required; continue standard monitoring."
            evidence = [
                f"Status={status}",
                f"CPU={cpu}%",
                f"Latency={latency}ms",
            ]

        return format_report(
            agent_name=self.name,
            summary=f"Evaluated {scenario.get('title', 'Incident')} using stateless threshold rules.",
            evidence=evidence,
            cause=cause,
            action=action,
            verification=[
                "Verify /health endpoint returns HTTP 200 OK",
                "Confirm error_rate_percent drops below 1%",
            ],
            limitations="Stateless: ignores deployment history, logs, and past incident outcomes.",
        )
