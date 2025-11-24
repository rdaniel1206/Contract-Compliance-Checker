from project.core.context_engineering import build_planner_context
from project.core.observability import log_event
from project.tools.tools import detect_contract_type

class Planner:
    NAME = "planner"
    def create_plan(self, user_input: str, sid: str):
        ctx = build_planner_context(user_input)
        ctype = detect_contract_type(ctx["summary"])
        checks = ["confidentiality_clause","liability_clause","termination_clause","governing_law_clause","data_protection_clause"]
        plan = {"session_id": sid, "contract_type": ctype, "checks": checks, "description": "Demo plan"}
        log_event(self.NAME, "PLAN_CREATED", {"session_id": sid, "plan": plan})
        return plan
