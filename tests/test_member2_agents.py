"""Member 2 tests only. Persistent feedback always uses temporary files."""

from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
import unittest

from agents.goal_based import GoalBasedAgent, meets_sla
from agents.utility_based import UtilityBasedAgent
from agents.learning_agent import DEFAULT_EXPERIENCE, LearningAgent
from schema import AgentReport


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = json.loads((ROOT / "data/scenarios.json").read_text())


class Member2AgentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.history = Path(self.temp.name) / "experience.json"
        self.history.write_bytes(DEFAULT_EXPERIENCE.read_bytes())
        self.learning = LearningAgent(self.history)
        self.agents = [GoalBasedAgent(), UtilityBasedAgent(), self.learning]

    def test_all_scenarios_have_exact_shared_report_schema_and_preserve_input(self):
        for key, scenario in SCENARIOS.items():
            original = deepcopy(scenario)
            for agent in self.agents:
                with self.subTest(scenario=key, agent=agent.name):
                    report = agent.analyze(scenario)
                    self.assertEqual(set(report), set(AgentReport.__annotations__))
                    for field, value in report.items():
                        if field in ("evidence", "verification_steps"):
                            self.assertIsInstance(value, list)
                            self.assertTrue(value)
                            self.assertTrue(all(isinstance(item, str) and item for item in value))
                        else:
                            self.assertIsInstance(value, str)
                            self.assertTrue(value)
                    self.assertEqual(scenario, original)

    def test_normal_scenario_needs_no_intervention(self):
        for agent in self.agents:
            self.assertIn("No intervention", agent.analyze(SCENARIOS["Normal_Baseline"])["recommended_action"])

    def test_pool_exhaustion_recommends_rollback_and_drain(self):
        for agent in self.agents:
            action = agent.analyze(SCENARIOS["Scenario_A"])["recommended_action"]
            self.assertIn("Roll back", action)
            self.assertIn("drain", action)

    def test_traffic_surge_distinguishes_goal_from_utility(self):
        scenario = SCENARIOS["Scenario_B"]
        self.assertIn("Horizontally scale", GoalBasedAgent().analyze(scenario)["recommended_action"])
        report = UtilityBasedAgent().analyze(scenario)
        self.assertIn("caching", report["recommended_action"])
        evidence = "\n".join(report["evidence"])
        self.assertIn("utility=57.00", evidence)  # .5*75 + .3*85 - .2*30
        self.assertIn("utility=55.50", evidence)  # .5*85 + .3*90 - .2*70
        self.assertIn("Horizontally scale", self.learning.analyze(scenario)["recommended_action"])

    def test_utility_weights_change_the_decision(self):
        speed_first = UtilityBasedAgent(speed_weight=0.9, safety_weight=0.1, cost_weight=0)
        self.assertIn("Horizontally scale", speed_first.analyze(SCENARIOS["Scenario_B"])["recommended_action"])
        for weights in [(-0.1, 0.9, 0.2), (1, 1, 1), (float("nan"), 0.3, 0.2)]:
            with self.assertRaises(ValueError):
                UtilityBasedAgent(*weights)

    def test_down_and_crash_loop_use_previous_healthy_version(self):
        for status in ["DOWN", "CRASH_LOOP"]:
            scenario = deepcopy(SCENARIOS["Scenario_C"])
            scenario["metrics"]["service_status"] = status
            for agent in self.agents:
                action = agent.analyze(scenario)["recommended_action"]
                self.assertIn("Roll back", action)
                self.assertIn("v2.1.0", action)

    def test_unhealthy_previous_version_is_never_a_rollback_candidate(self):
        scenario = deepcopy(SCENARIOS["Scenario_C"])
        scenario["previous_version"]["status"] = "UNHEALTHY"
        for agent in self.agents:
            report = agent.analyze(scenario)
            self.assertNotIn("Roll back", report["recommended_action"])
            self.assertIn("Correct and validate", report["recommended_action"])

    def test_all_sla_conditions_and_strict_boundaries(self):
        healthy = SCENARIOS["Normal_Baseline"]["metrics"]
        self.assertTrue(meets_sla(healthy))
        for change in [dict(latency_ms=200), dict(error_rate_percent=1), dict(service_status="DOWN", latency_ms=0)]:
            metrics = {**healthy, **change}
            self.assertFalse(meets_sla(metrics))
            scenario = deepcopy(SCENARIOS["Normal_Baseline"])
            scenario["metrics"] = metrics
            for agent in self.agents:
                self.assertIn("Escalate", agent.analyze(scenario)["recommended_action"])

    def test_unknown_bottleneck_escalates_instead_of_claiming_normal(self):
        scenario = deepcopy(SCENARIOS["Scenario_B"])
        scenario["metrics"]["requests_per_sec"] = 120
        for agent in self.agents:
            self.assertIn("Escalate", agent.analyze(scenario)["recommended_action"])

    def test_invalid_db_capacity_does_not_divide_by_zero(self):
        scenario = deepcopy(SCENARIOS["Scenario_B"])
        scenario["metrics"]["db_max_connections"] = 0
        for agent in self.agents:
            self.assertIn("Escalate", agent.analyze(scenario)["recommended_action"])

    def test_analysis_does_not_fabricate_feedback(self):
        before = self.history.read_bytes()
        for scenario in SCENARIOS.values():
            self.learning.analyze(scenario)
        self.assertEqual(self.history.read_bytes(), before)

    def test_recorded_failures_persist_and_change_selection(self):
        scenario = SCENARIOS["Scenario_B"]
        self.assertIn("Horizontally scale", self.learning.analyze(scenario)["recommended_action"])
        for _ in range(5):
            self.learning.record_outcome("Scenario_B", "scale_out", success=False)
        reloaded = LearningAgent(self.history)
        self.assertIn("caching", reloaded.analyze(scenario)["recommended_action"])
        counts = reloaded.record_outcome("Scenario_B", "scale_and_cache", success=True)
        self.assertEqual(counts, {"success": 3, "failure": 1})
        stored = json.loads(self.history.read_text())
        self.assertEqual(stored["Scenario_B"]["scale_out"], {"success": 5, "failure": 5})
        self.assertEqual(stored["Scenario_A"], json.loads(DEFAULT_EXPERIENCE.read_text())["Scenario_A"])

    def test_missing_history_and_unknown_case_use_cold_start(self):
        path = Path(self.temp.name) / "new" / "experience.json"
        agent = LearningAgent(path)
        report = agent.analyze(SCENARIOS["Scenario_B"], scenario_key="New_traffic_case")
        self.assertIn("Cold start", " ".join(report["evidence"]))
        self.assertIn("Horizontally scale", report["recommended_action"])
        agent.record_outcome("New_traffic_case", "scale_and_cache", True)
        self.assertIn("caching", agent.analyze(SCENARIOS["Scenario_B"], "New_traffic_case")["recommended_action"])

    def test_default_key_matches_each_shared_scenario_and_unknown_is_separate(self):
        for key, scenario in SCENARIOS.items():
            self.assertEqual(self.learning._scenario_key(scenario, None), key)
        unknown = deepcopy(SCENARIOS["Scenario_A"])
        unknown["metrics"]["latency_ms"] = 5000
        key = self.learning._scenario_key(unknown, None)
        self.assertTrue(key.startswith("unseen_"))
        self.assertEqual(key, self.learning._scenario_key(deepcopy(unknown), None))

    def test_default_history_is_relative_to_module_not_working_directory(self):
        old_cwd = Path.cwd()
        try:
            os.chdir(self.temp.name)
            agent = LearningAgent()
            self.assertEqual(agent.exp_path, DEFAULT_EXPERIENCE)
            self.assertIn("No intervention", agent.analyze(SCENARIOS["Normal_Baseline"])["recommended_action"])
            local = LearningAgent("local.json")
            local.record_outcome("new", "monitor", True)
            self.assertTrue(Path("local.json").exists())
        finally:
            os.chdir(old_cwd)

    def test_corrupt_history_is_rejected_without_overwrite(self):
        for invalid in ["{broken", "[]", '{"A": {"monitor": {"success": -1, "failure": 0}}}',
                        '{"A": {"monitor": {"success": true, "failure": 0}}}']:
            self.history.write_text(invalid)
            with self.assertRaises(ValueError):
                LearningAgent(self.history)
            self.assertEqual(self.history.read_text(), invalid)

    def test_invalid_feedback_cannot_change_history(self):
        original = self.history.read_bytes()
        for args in [("", "monitor", True), ("A", "invalid_action", True), ("A", "monitor", "success")]:
            with self.assertRaises(ValueError):
                self.learning.record_outcome(*args)
        self.assertEqual(self.history.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
