"""Planner Agent for contract analysis workflow planning and checklist generation."""

from typing import Dict, Any, List
from core.context_engineering import build_planner_context
from core.observability import log_event
from tools.tools import detect_contract_type

# Standard checklists tailored by contract type
CONTRACT_CHECKLISTS: Dict[str, List[str]] = {
    "NDA": [
        "confidentiality_clause",
        "termination_clause",
        "governing_law_clause",
        "indemnification_clause"
    ],
    "MSA": [
        "confidentiality_clause",
        "liability_clause",
        "indemnification_clause",
        "termination_clause",
        "governing_law_clause",
        "intellectual_property_clause",
        "payment_terms_clause",
        "warranties_disclaimers_clause",
        "force_majeure_clause"
    ],
    "SLA": [
        "termination_clause",
        "liability_clause",
        "payment_terms_clause",
        "force_majeure_clause",
        "governing_law_clause"
    ],
    "DPA": [
        "data_protection_clause",
        "confidentiality_clause",
        "liability_clause",
        "termination_clause",
        "governing_law_clause"
    ],
    "EMPLOYMENT": [
        "confidentiality_clause",
        "non_compete_clause",
        "termination_clause",
        "intellectual_property_clause",
        "governing_law_clause"
    ],
    "SAAS_AGREEMENT": [
        "data_protection_clause",
        "intellectual_property_clause",
        "liability_clause",
        "termination_clause",
        "warranties_disclaimers_clause",
        "governing_law_clause"
    ],
    "GENERIC_CONTRACT": [
        "confidentiality_clause",
        "liability_clause",
        "indemnification_clause",
        "termination_clause",
        "governing_law_clause",
        "data_protection_clause"
    ]
}

class Planner:
    """Planner agent responsible for analyzing contract intent and defining audit plans."""
    NAME = "planner"

    def create_plan(self, contract_text: str, sid: str) -> Dict[str, Any]:
        """Analyzes text and creates a compliance inspection plan."""
        ctx = build_planner_context(contract_text)
        ctype = ctx.get("contract_type") or detect_contract_type(contract_text)
        
        checks = CONTRACT_CHECKLISTS.get(ctype, CONTRACT_CHECKLISTS["GENERIC_CONTRACT"])
        
        plan = {
            "session_id": sid,
            "contract_type": ctype,
            "checks": checks,
            "document_stats": ctx.get("stats", {}),
            "description": f"Compliance audit plan for {ctype} ({len(checks)} clauses target)."
        }
        
        log_event(self.NAME, "PLAN_CREATED", {"session_id": sid, "plan": plan}, session_id=sid)
        return plan

    def handle_a2a_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """A2A protocol handler."""
        payload = message.get("payload", {})
        sid = message.get("session_id") or payload.get("session_id", "")
        text = payload.get("contract_text", "")
        plan = self.create_plan(text, sid)
        
        from core.a2a_protocol import make_plan_response
        return make_plan_response(sid, plan)

