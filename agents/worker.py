"""Worker Agent for executing contract compliance checks and clause extraction."""

from typing import Dict, Any
from core.context_engineering import build_worker_context
from core.observability import log_event
from tools.tools import analyze_full_contract

class Worker:
    """Worker agent that executes clause extraction, risk checks, and pattern evaluations."""
    NAME = "worker"

    def execute_plan(self, contract_text: str, plan: Dict[str, Any], sid: str) -> Dict[str, Any]:
        """Executes the analysis plan over contract text."""
        _ = build_worker_context(contract_text, plan)
        report = analyze_full_contract(plan, contract_text)
        
        out = {
            "session_id": sid,
            "plan": plan,
            "report": report
        }
        log_event(self.NAME, "WORK_COMPLETED", {
            "session_id": sid,
            "contract_type": report.get("contract_type"),
            "clauses_checked": len(report.get("clauses", [])),
            "red_flags": report.get("overall_risk", {}).get("total_red_flags", 0)
        }, session_id=sid)
        return out

    def handle_a2a_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """A2A protocol handler."""
        payload = message.get("payload", {})
        sid = message.get("session_id") or payload.get("session_id", "")
        plan = payload.get("plan", {})
        text = payload.get("contract_text", "")
        work_result = self.execute_plan(text, plan, sid)
        
        from core.a2a_protocol import make_work_response
        return make_work_response(sid, work_result)

