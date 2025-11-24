from project.core.context_engineering import build_evaluator_context
from project.core.observability import log_event

class Evaluator:
    NAME = "evaluator"
    def evaluate(self, text, plan, work, sid):
        _ = build_evaluator_context(text, plan, work)
        report = work.get("report", {})
        overall = report.get("overall_risk", {})
        score = overall.get("score", 0.0)
        level = overall.get("level", "LOW")

        final = f"Contract type: {plan.get('contract_type')}\nRisk: {level} (score {score})\nThis is a demo, not legal advice."

        result = {"session_id": sid, "final_response": final, "score": score, "level": level}
        log_event(self.NAME, "EVAL_COMPLETED", result)
        return result
