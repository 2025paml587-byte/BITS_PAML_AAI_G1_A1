"""Member 2: persistent outcome learning without inventing successful recoveries.

Integration: report = agent.analyze(scenario, scenario_key=selected_key).
After an action is actually evaluated, call
agent.record_outcome(selected_key, action_key, success=True/False).
Action keys and counts appear in report evidence. Analysis never updates counts.
Shipped counts are synthetic demonstration history, not production observations.
"""

import hashlib
import json
import os
from pathlib import Path
import tempfile

from schema import AgentReport, format_report
from agents.goal_based import VERIFICATION, meets_sla, recovery_options, telemetry_evidence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXPERIENCE = PROJECT_ROOT / "data" / "experience.json"
ACTION_KEYS = {
    "monitor", "rollback_config", "repair_config", "restart_service",
    "rollback_and_drain", "repair_queries", "increase_pool",
    "scale_out", "scale_and_cache", "rate_limit",
}


class LearningAgent:
    def __init__(self, exp_path=None):
        self.name = "Learning Agent"
        self.exp_path = Path(exp_path) if exp_path is not None else DEFAULT_EXPERIENCE
        if not self.exp_path.exists():
            self._write_history({})
        self._read_history()  # Reject corrupt history; do not silently overwrite it.

    def _read_history(self) -> dict:
        try:
            history = json.loads(self.exp_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid experience JSON: {self.exp_path}") from exc
        if not isinstance(history, dict):
            raise ValueError("Experience must map scenario keys to action counts.")
        for key, actions in history.items():
            if not key or not isinstance(actions, dict):
                raise ValueError("Each scenario must have an action dictionary.")
            for action, stats in actions.items():
                if action not in ACTION_KEYS or not isinstance(stats, dict) or set(stats) != {"success", "failure"}:
                    raise ValueError(f"Invalid experience action/counts: {key}/{action}")
                if any(type(value) is not int or value < 0 for value in stats.values()):
                    raise ValueError("Success/failure counts must be nonnegative integers.")
        return history

    def _write_history(self, history: dict) -> None:
        self.exp_path.parent.mkdir(parents=True, exist_ok=True)
        # Atomic replacement avoids partial JSON if a write is interrupted.
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.exp_path.parent,
                                             prefix=f".{self.exp_path.name}.", delete=False) as stream:
                temp_path = Path(stream.name)
                json.dump(history, stream, indent=2, sort_keys=True)
                stream.write("\n")
            os.replace(temp_path, self.exp_path)
        finally:
            if temp_path is not None and temp_path.exists():
                temp_path.unlink()

    def record_outcome(self, scenario_key: str, action_key: str, success: bool) -> dict:
        """Record one explicit observed/simulated outcome; return updated counts.

        Call once per evaluated action. This local JSON store assumes one writer;
        atomic file replacement does not provide concurrent update locking.
        """
        if not isinstance(scenario_key, str) or not scenario_key.strip():
            raise ValueError("A nonempty scenario key is required.")
        if action_key not in ACTION_KEYS:
            raise ValueError(f"Unknown action key: {action_key}")
        if type(success) is not bool:
            raise ValueError("success must be explicitly True or False.")
        history = self._read_history()
        stats = history.setdefault(scenario_key, {}).setdefault(action_key, {"success": 0, "failure": 0})
        stats["success" if success else "failure"] += 1
        self._write_history(history)
        return stats.copy()

    @staticmethod
    def _scenario_key(scenario: dict, scenario_key: str | None) -> str:
        if scenario_key is not None:
            if not isinstance(scenario_key, str) or not scenario_key.strip():
                raise ValueError("scenario_key must be a nonempty string.")
            return scenario_key
        # Preserve analyze(scenario) compatibility without defaulting every case to A.
        scenarios = json.loads((PROJECT_ROOT / "data" / "scenarios.json").read_text(encoding="utf-8"))
        for key, known in scenarios.items():
            if known == scenario:
                return key
        digest = hashlib.sha256(json.dumps(scenario, sort_keys=True).encode()).hexdigest()[:16]
        return f"unseen_{digest}"

    def analyze(self, scenario: dict, scenario_key: str | None = None) -> AgentReport:
        key = self._scenario_key(scenario, scenario_key)
        history = self._read_history().get(key, {})
        cause, plans = recovery_options(scenario)
        evidence = telemetry_evidence(scenario)
        evidence.append(f"Experience key={key}. Rank using (success + 1) / (success + failure + 2), a smoothed success estimate.")
        evidence.append("Shipped counts are synthetic demo history. Analysis does not assume success or change counts.")
        ranked = []
        for plan in plans:
            if plan.projected_state is None or not meets_sla(plan.projected_state):
                evidence.append(f"Excluded {plan.key}: recovery to all SLA goals is not predicted by the simulation model.")
                continue
            stats = history.get(plan.key, {"success": 0, "failure": 0})
            wins, losses = stats["success"], stats["failure"]
            estimate = (wins + 1) / (wins + losses + 2)
            evidence.append(f"Candidate {plan.key}: success={wins}, failure={losses}, smoothed estimate={estimate:.4f}.")
            ranked.append((estimate, plan, wins + losses))
        if ranked:
            estimate, selected, count = max(ranked, key=lambda item: item[0])
            action = selected.action
            evidence.append(f"Selected action_key={selected.key}, estimate={estimate:.4f}, recorded outcomes={count}; ties use declared order.")
            if not any(item[2] for item in ranked):
                evidence.append("Cold start: no eligible recorded outcomes; use the first goal-achieving plan until feedback arrives.")
        else:
            action = "Escalate to SRE for diagnosis; no supported goal-achieving action to learn from."
        return format_report(
            self.name, f"Experience-driven recovery for {scenario['title']}.", evidence, cause,
            action, list(VERIFICATION) + ["Call record_outcome(scenario_key, action_key, success) once the outcome is known."],
            "Synthetic seed history and small samples may mislead. Uses per-scenario counts without causal learning "
            "or exploration; candidate eligibility relies on a hand-authored model. JSON persistence assumes one writer.",
        )
