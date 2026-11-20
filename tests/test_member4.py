"""Member 4's packaging/readiness checks for submission.

This file verifies the Day 5 packaging deliverables that are Member 4's responsibility:
pinned dependencies, captured screenshots, and a minimal "does the app load"
smoke gate across all four scenarios.

Run with: python -m unittest tests.test_member4 -v
"""

import importlib
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from tests.member2_fixtures import SEED_HISTORY

ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS_PATH = ROOT / "requirements.txt"
SCREENSHOTS_DIR = ROOT / "screenshots"
SCENARIOS = json.loads((ROOT / "data/scenarios.json").read_text(encoding="utf-8"))

# pip distribution name -> importable module name, where they differ.
IMPORT_NAME_OVERRIDES = {
    "langchain-ollama": "langchain_ollama",
}

VERSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*==[A-Za-z0-9][A-Za-z0-9.]*$")


class Member4RequirementsTests(unittest.TestCase):
    """requirements.txt must be exactly pinned and every listed package installed."""

    def setUp(self):
        text = REQUIREMENTS_PATH.read_text(encoding="utf-8")
        self.lines = [line.strip() for line in text.splitlines() if line.strip()]

    def test_requirements_file_is_not_empty(self):
        self.assertTrue(self.lines, "requirements.txt must list at least one dependency")

    def test_every_requirement_is_exactly_pinned(self):
        unpinned = [line for line in self.lines if not VERSION_RE.match(line)]
        self.assertEqual(unpinned, [], f"Unpinned or malformed requirement(s): {unpinned}")

    def test_every_pinned_package_imports_successfully(self):
        failures = []
        for line in self.lines:
            package_name = line.split("==", 1)[0]
            module_name = IMPORT_NAME_OVERRIDES.get(package_name, package_name.replace("-", "_"))
            try:
                importlib.import_module(module_name)
            except ImportError as exc:
                failures.append(f"{package_name} (as {module_name}): {exc}")
        self.assertEqual(failures, [], f"Packages failed to import: {failures}")


class Member4ScreenshotsTests(unittest.TestCase):
    """screenshots/ must contain submission-ready evidence before packaging."""

    def setUp(self):
        self.files = [p.name for p in SCREENSHOTS_DIR.iterdir() if p.is_file()]
        self.image_files = [name for name in self.files if name.lower().endswith((".png", ".jpg", ".jpeg"))]

    def test_screenshots_directory_is_not_just_a_placeholder(self):
        self.assertTrue(self.image_files, "screenshots/ has no image files captured yet")

    def test_every_scenario_has_at_least_one_screenshot(self):
        lowered = [name.lower() for name in self.image_files]
        missing = []
        for key in SCENARIOS:
            # Normal_Baseline's committed screenshot is named "Baseline", not the
            # scenario key, so check both the raw key and its short form.
            short = key.replace("Normal_", "").replace("_", "-")
            if not any(short.lower() in name or key.lower() in name for name in lowered):
                missing.append(key)
        self.assertEqual(missing, [], f"No screenshot found for scenario(s): {missing}")

    def test_required_ui_sections_are_evidenced(self):
        lowered = [name.lower() for name in self.image_files]
        required_markers = {
            "agent tab": "agent-tab",
            "tool calling inspector": "toolinspector",
            "feedback simulator": "feedbacksimulator",
        }
        missing = [
            label for label, marker in required_markers.items()
            if not any(marker in name for name in lowered)
        ]
        self.assertEqual(missing, [], f"Missing screenshot evidence for: {missing}")


class Member4AppSmokeTests(unittest.TestCase):
    """Minimal 'does app.py load' gate across all 4 scenarios (offline, isolated history)."""

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        history_path = Path(temp.name) / "experience.json"
        history_path.write_text(json.dumps(SEED_HISTORY), encoding="utf-8")
        history_patch = patch("agents.learning_agent.DEFAULT_EXPERIENCE", history_path)
        history_patch.start()
        self.addCleanup(history_patch.stop)
        offline_patch = patch("agents.llm_agent.is_ollama_reachable", return_value=False)
        offline_patch.start()
        self.addCleanup(offline_patch.stop)

    def test_app_loads_and_runs_without_exceptions_for_every_scenario(self):
        for key in SCENARIOS:
            with self.subTest(scenario=key):
                app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
                self.assertFalse(list(app.exception), [item.message for item in app.exception])
                app.selectbox("scenario_key").select(key).run()
                app.button("run_agents").click().run()
                self.assertFalse(list(app.exception), [item.message for item in app.exception])
                self.assertEqual(len(app.session_state["last_reports"]), 6)


if __name__ == "__main__":
    unittest.main()
