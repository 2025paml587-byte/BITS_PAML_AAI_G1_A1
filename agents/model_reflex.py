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
        m = scenario.get("metrics", {})
        deploy_info = scenario.get("deployment_history", {})
        prev_info = scenario.get("previous_version", {})

        status = m.get("service_status", "UNKNOWN")
        cpu = m.get("cpu_percent", 0)
        latency = m.get("latency_ms", 0)
        rps = m.get("requests_per_sec", 0)
        db_active = m.get("db_active_connections", 0)
        db_max = max(1, m.get("db_max_connections", 100))

        deploy = deploy_info.get("last_change", "None")
        prev_ver = prev_info.get("version", "previous_stable")
        prev_status = prev_info.get("status", "UNKNOWN")

        # Calculate state deltas relative to internal baseline model
        traffic_ratio = round(rps / max(1, self.baseline["requests_per_sec"]), 1)
        db_util_pct = round((db_active / db_max) * 100, 1)
        recent_change = "None" not in deploy

        if status in ("CRASH_LOOP", "DOWN") and recent_change:
            cause = f"Startup crash correlated with recent deployment/config change ({deploy})."
            action = f"Roll back configuration/release to verified version {prev_ver}."
            evidence = [
                f"service_status={status}",
                f"Recent change detected: {deploy}",
                f"Previous version {prev_ver} status: {prev_status}",
            ]
        elif status in ("CRASH_LOOP", "DOWN") and not recent_change:
            cause = "Service crashed with no recent code or config changes detected."
            action = "Inspect host node health and redeploy container to a healthy node."
            evidence = [
                f"service_status={status}",
                "No recent deployment changes in history",
            ]
        elif db_active >= db_max:
            cause = (
                f"DB connection pool saturated ({db_util_pct}% vs {self.baseline['db_utilization_percent']}% baseline) "
                f"correlated with change ({deploy})."
            )
            action = f"Roll back recent change to {prev_ver} and drain stuck DB connections."
            evidence = [
                f"DB utilization={db_util_pct}% (baseline: {self.baseline['db_utilization_percent']}%)",
                f"Latency={latency}ms (baseline: {self.baseline['latency_ms']}ms)",
                f"Deployment history: {deploy}",
            ]
        elif cpu > 85 and traffic_ratio > 3.0 and db_util_pct < 70:
            cause = (
                f"Organic traffic surge ({traffic_ratio}x baseline) saturating CPU while DB pool remains healthy ({db_util_pct}%)."
            )
            action = "Trigger horizontal auto-scaling and enable edge rate limiting."
            evidence = [
                f"Traffic={rps} req/s ({traffic_ratio}x baseline)",
                f"CPU={cpu}% (baseline: {self.baseline['cpu_percent']}%)",
                f"DB pool healthy at {db_util_pct}%",
            ]
        elif cpu > 85 and traffic_ratio <= 3.0:
            cause = f"CPU saturation ({cpu}%) without proportional traffic spike ({traffic_ratio}x baseline), indicating an internal runaway process."
            action = "Capture thread/CPU profile and perform a rolling restart of affected workers."
            evidence = [
                f"CPU={cpu}% (baseline: {self.baseline['cpu_percent']}%)",
                f"Traffic={traffic_ratio}x baseline (normal load)",
            ]
        else:
            cause = "Observed telemetry aligns with internal healthy baseline model."
            action = "Maintain current state and continue baseline tracking."
            evidence = [
                f"CPU={cpu}% vs {self.baseline['cpu_percent']}% baseline",
                f"Latency={latency}ms vs {self.baseline['latency_ms']}ms baseline",
            ]

        return format_report(
            agent_name=self.name,
            summary=f"State-delta and deployment correlation analysis for {scenario.get('title', 'Incident')}.",
            evidence=evidence,
            cause=cause,
            action=action,
            verification=[
                "Confirm metrics return within 15% of internal baseline model",
                "Verify zero crash loops or pool exhaustion alerts",
            ],
            limitations="Relies on static baseline assumptions; does not weigh multi-action cost trade-offs or learn from outcomes.",
        )
