from project.tools.tools import summarize_text

def build_planner_context(text):
    return {"summary": summarize_text(text,200), "raw_input": text}
def build_worker_context(text, plan):
    return {"raw_input": text, "plan": plan}
def build_evaluator_context(text, plan, work):
    return {"raw_input": text, "plan": plan, "work_result": work}
