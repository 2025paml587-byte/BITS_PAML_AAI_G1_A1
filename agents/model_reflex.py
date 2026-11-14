from schema import format_report, AgentReport


class ModelBasedReflexAgent:
    def __init__(self):
        self.name = "Model-Based Reflex Agent"
        # Internal model of normal system operating state
        self.baseline = {
            "cpu_percent": 30,
            "requests_per_sec": 130,
            "latency_ms": 50,
            "db_utilization_percent": 25,
        }

    def analyze(self, scenario: dict) -> AgentReport:
        m = scenario["metrics"]
        deploy = scenario["deployment_history"]["last_change"]
        prev_ver = scenario["previous_version"]["version"]

        # Calculate state deltas relative to internal baseline model
        traffic_ratio = round(m["requests_per_sec"] / self.baseline["requests_per_sec"], 1)
        db_util_pct = round((m["db_active_connections"] / m["db_max_connections"]) * 100, 1)
        recent_change = "None" not in deploy

        if m["service_status"] in ("CRASH_LOOP", "DOWN") and recent_change:
            cause = f"Startup crash correlated with recent deployment/config change ({deploy})."
            action = f"Roll back configuration/release to verified version {prev_ver}."
            evidence = [
                f"service_status={m['service_status']}",
                f"Recent change detected: {deploy}",
                f"Previous version {prev_ver} status: {scenario['previous_version']['status']}",
            ]
        elif m["db_active_connections"] >= m["db_max_connections"]:
            cause = (
                f"DB connection pool saturated ({db_util_pct}% vs {self.baseline['db_utilization_percent']}% baseline) "
                f"following recent change ({deploy})."
            )
            action = f"Roll back recent change to {prev_ver} and drain stuck DB connections."
            evidence = [
                f"DB utilization={db_util_pct}% (baseline: {self.baseline['db_utilization_percent']}%)",
                f"Latency={m['latency_ms']}ms (baseline: {self.baseline['latency_ms']}ms)",
                f"Deployment history: {deploy}",
            ]
        elif m["cpu_percent"] > 85 and traffic_ratio > 3.0 and db_util_pct < 70:
            cause = (
                f"Organic traffic surge ({traffic_ratio}x baseline) saturating CPU while DB pool remains healthy ({db_util_pct}%)."
            )
            action = "Trigger horizontal auto-scaling and enable edge rate limiting."
            evidence = [
                f"Traffic={m['requests_per_sec']} req/s ({traffic_ratio}x baseline)",
                f"CPU={m['cpu_percent']}% (baseline: {self.baseline['cpu_percent']}%)",
                f"DB pool healthy at {db_util_pct}%",
            ]
        else:
            cause = "Observed telemetry aligns with internal healthy baseline model."
            action = "Maintain current state and continue baseline tracking."
            evidence = [
                f"CPU={m['cpu_percent']}% vs {self.baseline['cpu_percent']}% baseline",
                f"Latency={m['latency_ms']}ms vs {self.baseline['latency_ms']}ms baseline",
            ]

        return format_report(
            agent_name=self.name,
            summary=f"State-delta and deployment correlation analysis for {scenario['title']}.",
            evidence=evidence,
            cause=cause,
            action=action,
            verification=[
                "Confirm metrics return within 15% of internal baseline model",
                "Verify zero crash loops or pool exhaustion alerts",
            ],
            limitations="Relies on static baseline assumptions; does not weigh multi-action cost trade-offs or learn from outcomes.",
        )
