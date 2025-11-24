from project.core.context_engineering import build_worker_context
from project.core.observability import log_event
from project.tools.tools import generate_dummy_clause_report

class Worker:
    NAME = "worker"
    def execute_plan(self, text: str, plan, sid):
        _ = build_worker_context(text, plan)
        rep = generate_dummy_clause_report(plan, text)
        out = {"session_id": sid, "plan": plan, "report": rep}
        log_event(self.NAME, "WORK_COMPLETED", out)
        return out
