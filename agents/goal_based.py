"""Member 2: compare simulated action outcomes against an explicit SLA goal.

The action model is illustrative, not a production recovery guarantee. These
agents recommend actions; they never execute them. Utility and learning agents
reuse this candidate vocabulary so their decisions can be compared fairly.
"""

from dataclasses import dataclass

from schema import AgentReport, format_report


@dataclass(frozen=True)
class RecoveryPlan:
    key: str
    action: str
    projected_state: dict | None
    speed: float
    safety: float
    cost: float


def meets_sla(metrics: dict) -> bool:
    """Zero latency during an outage must not count as recovery."""
    return (
        metrics["service_status"] == "RUNNING"
        and 0 <= metrics["error_rate_percent"] < 1
        and 0 <= metrics["latency_ms"] < 200
    )


def recovery_options(scenario: dict) -> tuple[str, list[RecoveryPlan]]:
    """Build applicable plans with explicit, hand-authored outcome estimates.

    Speed, safety and cost are illustrative ratings on a 0..100 scale; higher
    cost is worse. A missing projected state means recovery is not established.
    The first goal-achieving plan provides deterministic goal-agent tie breaking.
    """
    m = scenario["metrics"]
    previous = scenario.get("previous_version", {})
    change = scenario.get("deployment_history", {}).get("last_change", "")
    recent_change = bool(change.strip()) and not change.lower().startswith("none")
    rollback_available = previous.get("status") == "HEALTHY" and bool(previous.get("version"))
    recovered = {"service_status": "RUNNING", "latency_ms": 100, "error_rate_percent": 0.2}
    current = {key: m[key] for key in recovered}
    plans = [RecoveryPlan("monitor", "No intervention; continue monitoring.", current, 100, 100, 0)]
    if meets_sla(m):
        return "All three target SLA conditions are already satisfied.", plans

    if m["service_status"] in ("DOWN", "CRASH_LOOP"):
        cause = "Service outage blocks the RUNNING goal."
        if recent_change:
            cause += f" It follows a reported change: {change}."
        if rollback_available and recent_change:
            plans.append(RecoveryPlan(
                "rollback_config", f"Roll back configuration/release to verified healthy version {previous['version']}.",
                recovered.copy(), 90, 90, 15,
            ))
        config_error = any("config" in line.lower() for line in scenario.get("logs", []))
        if config_error:
            plans.append(RecoveryPlan(
                "repair_config", "Correct and validate the reported configuration error, then redeploy.",
                recovered.copy(), 45, 75, 10,
            ))
        plans.append(RecoveryPlan(
            "restart_service", "Restart the service container and check startup logs.",
            None, 95, 40, 10,
        ))
    elif m["db_max_connections"] > 0 and m["db_active_connections"] >= m["db_max_connections"]:
        cause = "Database pool exhaustion prevents requests from meeting latency and error goals."
        if rollback_available and recent_change:
            plans.append(RecoveryPlan(
                "rollback_and_drain", f"Roll back the recent patch to {previous['version']} and drain stuck DB connections.",
                recovered.copy(), 85, 90, 20,
            ))
        plans.extend([
            RecoveryPlan("repair_queries", "Identify and fix blocking queries, then recycle affected DB connections.",
                         recovered.copy(), 45, 95, 15),
            RecoveryPlan("increase_pool", "Increase DB pool capacity after checking database headroom.",
                         None, 95, 45, 65),
        ])
    elif (
        m["cpu_percent"] > 85 and m["requests_per_sec"] > 3 * 130
        and m["db_max_connections"] > 0
        and m["db_active_connections"] / m["db_max_connections"] < 0.7
    ):
        cause = "High traffic and CPU with a healthy DB pool suggest a compute bottleneck."
        plans.extend([
            RecoveryPlan("scale_out", "Horizontally scale service replicas and verify capacity under current traffic.",
                         recovered.copy(), 85, 90, 70),
            RecoveryPlan("scale_and_cache", "Scale service replicas and enable caching for cacheable requests.",
                         recovered.copy(), 75, 85, 30),
            RecoveryPlan("rate_limit", "Apply strict rate limiting to reduce incoming load.",
                         {"service_status": "RUNNING", "latency_ms": 150, "error_rate_percent": 5},
                         95, 50, 5),
        ])
    else:
        cause = "SLA violation has no supported recovery model in the supplied telemetry."
    return cause, plans


def telemetry_evidence(scenario: dict) -> list[str]:
    m = scenario["metrics"]
    previous = scenario.get("previous_version", {})
    return [
        f"Observed status={m['service_status']}, latency={m['latency_ms']}ms, errors={m['error_rate_percent']}%.",
        f"CPU={m['cpu_percent']}%, traffic={m['requests_per_sec']} req/s, DB={m['db_active_connections']}/{m['db_max_connections']}.",
        f"Last change: {scenario.get('deployment_history', {}).get('last_change', 'unknown')}.",
        f"Previous version={previous.get('version', 'unknown')}, health={previous.get('status', 'unknown')}.",
        *[f"Observed log: {line}" for line in scenario.get("logs", [])],
    ]


VERIFICATION = [
    "Verify service_status=RUNNING and /health returns HTTP 200.",
    "Measure error_rate_percent < 1% and latency_ms < 200 under representative traffic.",
    "Confirm crash loops and DB pool exhaustion have cleared; record the observed outcome.",
]


class GoalBasedAgent:
    def __init__(self):
        self.name = "Goal-Based Agent"
        self.goal = "service_status=RUNNING, error_rate_percent < 1%, latency_ms < 200"

    def analyze(self, scenario: dict) -> AgentReport:
        cause, plans = recovery_options(scenario)
        evidence = telemetry_evidence(scenario)
        evidence.append(f"Goal: {self.goal}. Projected outcomes below are simulation assumptions.")
        feasible = []
        for plan in plans:
            achieves_goal = plan.projected_state is not None and meets_sla(plan.projected_state)
            evidence.append(f"Candidate {plan.key}: projected={plan.projected_state}; achieves all goals={achieves_goal}.")
            if achieves_goal:
                feasible.append(plan)
        action = feasible[0].action if feasible else "Escalate to SRE for diagnosis; no candidate is predicted to satisfy all SLA goals."
        evidence.append("Select the first goal-achieving plan in declared order; cost and risk do not break ties.")
        return format_report(
            self.name, f"SLA goal evaluation for {scenario['title']}.", evidence, cause,
            action, list(VERIFICATION),
            "Uses hand-authored, single-step outcome predictions, not measured recovery results. "
            "Ignores cost/risk trade-offs among goal-achieving plans; limited to modeled incident types.",
        )
