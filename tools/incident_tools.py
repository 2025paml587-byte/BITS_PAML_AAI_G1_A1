"""Incident response investigation tools for LangChain LLM agent.

Owner: Member 3 (Sourav) - LLM & LangChain Engineer
Provides four standardized LangChain @tool functions allowing the LLM
to inspect real-time metrics, logs, deployment history, and prior release health.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from langchain_core.tools import tool

# Resolve scenarios.json path robustly relative to repository root
REPO_ROOT = Path(__file__).resolve().parents[1]
SCENARIOS_PATH = REPO_ROOT / "data" / "scenarios.json"


def load_scenarios() -> Dict[str, Any]:
    """Load scenarios from disk or return fallback dictionary."""
    if SCENARIOS_PATH.is_file():
        try:
            return json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


# Cache loaded scenarios; reload if path changes or empty
SCENARIOS = load_scenarios()


def _get_scenario_or_raise(scenario_key: str) -> Dict[str, Any]:
    """Retrieve scenario dictionary for given key, refreshing cache if needed."""
    global SCENARIOS
    if scenario_key not in SCENARIOS:
        SCENARIOS = load_scenarios()
    if scenario_key not in SCENARIOS:
        # Match case-insensitively as fallback
        for k, v in SCENARIOS.items():
            if k.lower() == scenario_key.lower():
                return v
        raise KeyError(
            f"Scenario '{scenario_key}' not found in scenarios database. "
            f"Available scenarios: {list(SCENARIOS.keys())}"
        )
    return SCENARIOS[scenario_key]


@tool
def get_metrics(scenario_key: str) -> str:
    """Fetch current system metrics for a scenario.

    Returns JSON containing service_status, cpu_percent, latency_ms,
    error_rate_percent, requests_per_sec, db_active_connections,
    and db_max_connections.
    """
    try:
        data = _get_scenario_or_raise(scenario_key)
        return json.dumps(data.get("metrics", {}), indent=2)
    except Exception as exc:
        return json.dumps({"error": str(exc)})


@tool
def search_logs(scenario_key: str, query: str = "") -> str:
    """Search recent application, error, and system logs for a scenario.

    Optional query string filters log lines case-insensitively.
    Returns JSON list of matching log messages.
    """
    try:
        data = _get_scenario_or_raise(scenario_key)
        logs: List[str] = data.get("logs", [])
        if query:
            q_lower = query.strip().lower()
            filtered = [line for line in logs if q_lower in line.lower()]
            return json.dumps(filtered if filtered else logs, indent=2)
        return json.dumps(logs, indent=2)
    except Exception as exc:
        return json.dumps({"error": str(exc)})


@tool
def get_deployment_history(scenario_key: str) -> str:
    """Retrieve recent deployment details, commit changes, and authors for a scenario.

    Returns JSON containing current_version, last_change description,
    and changed_by identity.
    """
    try:
        data = _get_scenario_or_raise(scenario_key)
        return json.dumps(data.get("deployment_history", {}), indent=2)
    except Exception as exc:
        return json.dumps({"error": str(exc)})


@tool
def check_previous_version(scenario_key: str) -> str:
    """Check the release version and health verification status of the prior build.

    Returns JSON containing previous version tag and status (e.g. HEALTHY).
    """
    try:
        data = _get_scenario_or_raise(scenario_key)
        return json.dumps(data.get("previous_version", {}), indent=2)
    except Exception as exc:
        return json.dumps({"error": str(exc)})
