from typing import List, TypedDict

class AgentReport(TypedDict):
    agent_name: str
    incident_summary: str
    evidence: List[str]
    likely_cause: str
    recommended_action: str
    verification_steps: List[str]
    limitations: str

def format_report(
    agent_name: str,
    summary: str,
    evidence: List[str],
    cause: str,
    action: str,
    verification: List[str],
    limitations: str
) -> AgentReport:
    return {
        "agent_name": agent_name,
        "incident_summary": summary,
        "evidence": evidence,
        "likely_cause": cause,
        "recommended_action": action,
        "verification_steps": verification,
        "limitations": limitations,
    }
