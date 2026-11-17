"""Member 3 (Sourav) Unit & Integration Test Suite.

Tests tools/incident_tools.py and agents/llm_agent.py:
1. Validates all 4 LangChain @tool functions against all scenarios.
2. Validates LLMIncidentAgent schema compliance (exact 7 keys in AgentReport).
3. Asserts >= 2 tool invocations per incident analysis.
4. Validates evidence grounding, cause identification, and actionable verification.
5. Tests offline fallback resilience and both invocation call styles.
6. Validates cross-agent pipeline execution alongside Member 1 & Member 2 agents.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from agents.goal_based import GoalBasedAgent
from agents.learning_agent import LearningAgent
from agents.llm_agent import LLMIncidentAgent
from agents.model_reflex import ModelBasedReflexAgent
from agents.simple_reflex import SimpleReflexAgent
from agents.utility_based import UtilityBasedAgent
from schema import AgentReport
from tools.incident_tools import (
    check_previous_version,
    get_deployment_history,
    get_metrics,
    search_logs,
)

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS_PATH = ROOT / "data" / "scenarios.json"
SCENARIOS = json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))


class Member3ToolsTests(unittest.TestCase):
    """Unit tests for the 4 LangChain tools in tools/incident_tools.py."""

    def test_get_metrics_returns_valid_json_for_all_scenarios(self):
        for key in SCENARIOS:
            with self.subTest(scenario=key):
                raw = get_metrics.invoke({"scenario_key": key})
                metrics = json.loads(raw)
                self.assertIn("service_status", metrics)
                self.assertIn("cpu_percent", metrics)
                self.assertIn("latency_ms", metrics)
                self.assertIn("error_rate_percent", metrics)
                self.assertIn("db_active_connections", metrics)

    def test_search_logs_filters_correctly(self):
        # Scenario A has connection pool error
        logs_a = json.loads(search_logs.invoke({"scenario_key": "Scenario_A", "query": "pool"}))
        self.assertTrue(any("connection pool exhausted" in line.lower() for line in logs_a))

        # Scenario C has config parse error
        logs_c = json.loads(search_logs.invoke({"scenario_key": "Scenario_C", "query": "config"}))
        self.assertTrue(any("config" in line.lower() for line in logs_c))

        # Unfiltered returns all logs
        logs_all = json.loads(search_logs.invoke({"scenario_key": "Normal_Baseline"}))
        self.assertGreater(len(logs_all), 0)

    def test_get_deployment_history_structure(self):
        for key in SCENARIOS:
            with self.subTest(scenario=key):
                raw = get_deployment_history.invoke({"scenario_key": key})
                deploy = json.loads(raw)
                self.assertIn("current_version", deploy)
                self.assertIn("last_change", deploy)

    def test_check_previous_version_structure(self):
        for key in SCENARIOS:
            with self.subTest(scenario=key):
                raw = check_previous_version.invoke({"scenario_key": key})
                prev = json.loads(raw)
                self.assertIn("version", prev)
                self.assertIn("status", prev)

    def test_unknown_scenario_returns_error_json(self):
        raw = get_metrics.invoke({"scenario_key": "NonExistentScenario_XYZ"})
        data = json.loads(raw)
        self.assertIn("error", data)


class Member3LLMAgentTests(unittest.TestCase):
    """Unit and behavioral tests for LLMIncidentAgent in agents/llm_agent.py."""

    def setUp(self):
        self.agent = LLMIncidentAgent(model_name="qwen2.5:3b", fallback_on_error=True)

    def test_exact_agent_report_schema_and_immutability(self):
        for key, scenario in SCENARIOS.items():
            original = deepcopy(scenario)
            with self.subTest(scenario=key):
                report, tools_called = self.agent.analyze(key, scenario["title"])

                # Check exact TypedDict keys
                self.assertEqual(set(report), set(AgentReport.__annotations__))

                # Evidence & Verification must be non-empty lists of strings
                self.assertIsInstance(report["evidence"], list)
                self.assertGreater(len(report["evidence"]), 0)
                self.assertTrue(all(isinstance(e, str) and len(e) > 0 for e in report["evidence"]))

                self.assertIsInstance(report["verification_steps"], list)
                self.assertGreater(len(report["verification_steps"]), 0)
                self.assertTrue(all(isinstance(v, str) and len(v) > 0 for v in report["verification_steps"]))

                # Other fields must be non-empty strings
                for field in ("agent_name", "incident_summary", "likely_cause", "recommended_action", "limitations"):
                    self.assertIsInstance(report[field], str)
                    self.assertTrue(report[field].strip())

                # Preserves input data
                self.assertEqual(scenario, original)

    def test_enforces_at_least_two_tool_calls(self):
        for key, scenario in SCENARIOS.items():
            with self.subTest(scenario=key):
                report, tools_called = self.agent.analyze(key, scenario["title"])
                self.assertGreaterEqual(
                    len(tools_called),
                    2,
                    f"Expected >= 2 tool calls for {key}, but got {len(tools_called)}: {tools_called}",
                )

    def test_flexible_invocation_styles(self):
        # Style 1: analyze(selected_key, scenario["title"]) - used by Template 6 app.py
        r1, t1 = self.agent.analyze("Scenario_A", SCENARIOS["Scenario_A"]["title"])
        self.assertIn("Scenario_A", r1["incident_summary"])

        # Style 2: analyze(scenario, scenario_key=key) - used by batch runner loops
        r2, t2 = self.agent.analyze(SCENARIOS["Scenario_A"], scenario_key="Scenario_A")
        self.assertIn("Scenario_A", r2["incident_summary"])

    def test_scenario_a_recommends_rollback_and_drain(self):
        report, _ = self.agent.analyze("Scenario_A", SCENARIOS["Scenario_A"]["title"])
        action = report["recommended_action"].lower()
        cause = report["likely_cause"].lower()
        self.assertTrue("pool" in action or "pool" in cause or "drain" in action or "rollback" in action)

    def test_scenario_b_recommends_scaling_not_db_restart(self):
        report, _ = self.agent.analyze("Scenario_B", SCENARIOS["Scenario_B"]["title"])
        action = report["recommended_action"].lower()
        self.assertTrue("scale" in action or "auto-scaling" in action or "rate" in action)

    def test_scenario_c_recommends_config_rollback(self):
        report, _ = self.agent.analyze("Scenario_C", SCENARIOS["Scenario_C"]["title"])
        action = report["recommended_action"].lower()
        self.assertTrue("roll" in action or "v2.1.0" in action)

    def test_normal_baseline_recommends_monitoring(self):
        report, _ = self.agent.analyze("Normal_Baseline", SCENARIOS["Normal_Baseline"]["title"])
        action = report["recommended_action"].lower()
        self.assertTrue("no" in action or "monitor" in action or "maintain" in action)


class CrossAgentPipelineIntegrationTests(unittest.TestCase):
    """Validates that all 6 agents can execute together sequentially on identical inputs."""

    def test_all_six_agents_execute_without_collision(self):
        agents = [
            SimpleReflexAgent(),
            ModelBasedReflexAgent(),
            GoalBasedAgent(),
            UtilityBasedAgent(),
            LearningAgent(),
            LLMIncidentAgent(),
        ]

        for s_key, s_data in SCENARIOS.items():
            reports = []
            for agent in agents:
                if isinstance(agent, LLMIncidentAgent):
                    rep, tools = agent.analyze(s_key, s_data["title"])
                elif isinstance(agent, LearningAgent):
                    rep = agent.analyze(s_data, scenario_key=s_key)
                else:
                    rep = agent.analyze(s_data)
                reports.append(rep)

            self.assertEqual(len(reports), 6)
            for r in reports:
                self.assertEqual(set(r.keys()), set(AgentReport.__annotations__))


if __name__ == "__main__":
    unittest.main()
