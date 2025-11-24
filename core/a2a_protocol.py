import uuid
def _msg(sender, receiver, type_, payload):
    return {"id": str(uuid.uuid4()), "sender": sender, "receiver": receiver, "message_type": type_, "payload": payload}

def make_plan_request(sid, text):
    return _msg("main_agent", "planner", "PLAN_REQUEST", {"session_id": sid, "user_input": text})
def make_plan_response(sid, plan):
    return _msg("planner", "main_agent", "PLAN_RESPONSE", {"session_id": sid, "plan": plan})

def make_work_request(sid, plan, text):
    return _msg("main_agent", "worker", "WORK_REQUEST", {"session_id": sid, "plan": plan, "user_input": text})
def make_work_response(sid, res):
    return _msg("worker", "main_agent", "WORK_RESPONSE", {"session_id": sid, "work_result": res})

def make_eval_request(sid, plan, work, text):
    return _msg("main_agent", "evaluator", "EVAL_REQUEST", {"session_id": sid, "plan": plan, "work_result": work, "user_input": text})
def make_eval_response(sid, out):
    return _msg("evaluator", "main_agent", "EVAL_RESPONSE", {"session_id": sid, "final_result": out})
