"""Member 2's shared UI integration checks; no live Ollama or real history writes.

Run with: python -m unittest tests.test_member2_ui -v
AppTest drives the real app, five classical agents, and Member 3's real tools and
offline fallback. Only Ollama availability and the experience path are patched.
"""

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from agents.learning_agent import LearningAgent
from agents.llm_agent import LLMIncidentAgent
from schema import AgentReport
from tests.member2_fixtures import SEED_HISTORY


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = json.loads((ROOT / "data/scenarios.json").read_text(encoding="utf-8"))


class Member2UIIntegrationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.history_path = Path(temp.name) / "experience.json"
        self.history_path.write_text(json.dumps(SEED_HISTORY), encoding="utf-8")
        history_patch = patch("agents.learning_agent.DEFAULT_EXPERIENCE", self.history_path)
        history_patch.start()
        self.addCleanup(history_patch.stop)
        offline_patch = patch("agents.llm_agent.is_ollama_reachable", return_value=False)
        offline_patch.start()
        self.addCleanup(offline_patch.stop)
        # Count real calls so feedback can be checked not to rerun the LLM path.
        llm_patch = patch.object(LLMIncidentAgent, "analyze", autospec=True, side_effect=LLMIncidentAgent.analyze)
        self.llm_calls = llm_patch.start()
        self.addCleanup(llm_patch.stop)

    def assert_no_app_errors(self, app):
        self.assertFalse(list(app.exception), [item.message for item in app.exception])

    def start_app(self, key="Normal_Baseline"):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
        self.assert_no_app_errors(app)
        app.selectbox("scenario_key").select(key).run()
        app.button("run_agents").click().run()
        self.assert_no_app_errors(app)
        return app

    @staticmethod
    def learning_report(app):
        return next(report for report in app.session_state["last_reports"]
                    if report["agent_name"] == "Learning Agent")

    def test_all_four_scenarios_render_six_reports_and_applicable_feedback(self):
        for key, scenario in SCENARIOS.items():
            with self.subTest(scenario=key):
                app = self.start_app(key)
                reports = app.session_state["last_reports"]
                self.assertEqual(len(reports), 6)
                for report in reports:
                    self.assertEqual(set(report), set(AgentReport.__annotations__))
                    self.assertIn(scenario["title"], report["incident_summary"])
                table = app.dataframe[0].value
                self.assertEqual(len(table), 6)
                self.assertEqual(table["Recommended Action"].tolist(), [r["recommended_action"] for r in reports])
                self.assertTrue(all(table["Architectural Limitations"]))
                self.assertGreaterEqual(len(app.session_state["tools_used"]), 2)
                expected = LearningAgent.feedback_actions(scenario)
                dropdown = app.selectbox(f"feedback_action_{key}")
                self.assertEqual(dropdown.options, list(expected.values()))
                self.assertIn(dropdown.value, expected)
        self.assertEqual(json.loads(self.history_path.read_text()), SEED_HISTORY)

    def test_feedback_persists_once_and_refreshes_report_and_comparison(self):
        app = self.start_app("Scenario_B")
        original_reports = deepcopy(app.session_state["last_reports"])
        original_tools = list(app.session_state["tools_used"])
        self.assertIn("Horizontally scale", self.learning_report(app)["recommended_action"])
        app.selectbox("feedback_action_Scenario_B").select("scale_out").run()
        for count in range(1, 6):
            app.button("record_failure").click().run()
            self.assert_no_app_errors(app)
            self.assertEqual(json.loads(self.history_path.read_text())["Scenario_B"]["scale_out"]["failure"], count)
        self.assertIn("caching", self.learning_report(app)["recommended_action"])
        table = app.dataframe[0].value
        learning_row = table[table["Agent Architecture"] == "Learning Agent"].iloc[0]
        self.assertEqual(learning_row["Recommended Action"], self.learning_report(app)["recommended_action"])
        self.assertEqual(app.session_state["tools_used"], original_tools)
        self.assertEqual(self.llm_calls.call_count, 1)
        for old, new in zip(original_reports, app.session_state["last_reports"]):
            if old["agent_name"] != "Learning Agent":
                self.assertEqual(old, new)

        # An ordinary rerun must not replay the previous feedback event.
        saved = self.history_path.read_bytes()
        app.run()
        self.assertEqual(self.history_path.read_bytes(), saved)
        reloaded = LearningAgent(self.history_path)
        self.assertIn("caching", reloaded.analyze(SCENARIOS["Scenario_B"], "Scenario_B")["recommended_action"])

    def test_normal_and_database_feedback_can_be_recorded(self):
        for key, action in [("Normal_Baseline", "monitor"), ("Scenario_A", "rollback_and_drain")]:
            with self.subTest(scenario=key):
                app = self.start_app(key)
                app.selectbox(f"feedback_action_{key}").select(action).run()
                app.button("record_success").click().run()
                self.assert_no_app_errors(app)
                stats = json.loads(self.history_path.read_text())[key][action]
                self.assertEqual(stats["success"], SEED_HISTORY[key][action]["success"] + 1)
                self.assertTrue(any("Recorded one success" in item.value for item in app.success))

    def test_switching_scenario_clears_old_reports_and_feedback(self):
        app = self.start_app("Scenario_A")
        app.selectbox("scenario_key").select("Scenario_B").run()
        self.assert_no_app_errors(app)
        self.assertNotIn("last_reports", app.session_state)
        self.assertEqual(len(app.dataframe), 0)
        self.assertNotIn("record_success", [item.key for item in app.button])
        app.button("run_agents").click().run()
        self.assert_no_app_errors(app)
        self.assertEqual(app.session_state["active_key"], "Scenario_B")
        self.assertTrue(all(SCENARIOS["Scenario_B"]["title"] in r["incident_summary"]
                            for r in app.session_state["last_reports"]))
        self.assertEqual(app.selectbox("feedback_action_Scenario_B").value, "scale_out")
        app.button("record_failure").click().run()
        stored = json.loads(self.history_path.read_text())
        self.assertEqual(stored["Scenario_A"], SEED_HISTORY["Scenario_A"])
        self.assertEqual(stored["Scenario_B"]["scale_out"]["failure"], 1)

    def test_switching_model_requires_new_reports(self):
        app = self.start_app()
        app.selectbox("model_choice").select("qwen3:4b").run()
        self.assert_no_app_errors(app)
        self.assertNotIn("last_reports", app.session_state)
        self.assertEqual(len(app.dataframe), 0)
        app.button("run_agents").click().run()
        self.assert_no_app_errors(app)
        self.assertEqual(app.session_state["active_model"], "qwen3:4b")
        self.assertIn("qwen3:4b", app.session_state["last_reports"][-1]["agent_name"])

    def test_no_eligible_action_disables_feedback(self):
        with patch.object(LearningAgent, "feedback_actions", return_value={}):
            app = self.start_app()
            self.assertNotIn("record_success", [item.key for item in app.button])
            self.assertTrue(any("feedback is unavailable" in item.value for item in app.info))
            self.assertEqual(json.loads(self.history_path.read_text()), SEED_HISTORY)

    def test_corrupt_history_feedback_shows_error_without_overwrite(self):
        app = self.start_app()
        self.history_path.write_text("{broken", encoding="utf-8")
        app.button("record_success").click().run()
        self.assert_no_app_errors(app)
        self.assertTrue(any("Feedback was not saved" in item.value for item in app.error))
        self.assertEqual(self.history_path.read_text(), "{broken")


if __name__ == "__main__":
    unittest.main()
