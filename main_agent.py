from project.agents.planner import Planner
from project.agents.worker import Worker
from project.agents.evaluator import Evaluator
from project.memory.session_memory import SessionMemory
from project.core.observability import log_event
from project.core import a2a_protocol as protocol

class MainAgent:
    NAME = "main_agent"
    def __init__(self):
        self.planner = Planner()
        self.worker = Worker()
        self.evaluator = Evaluator()

    def handle_message(self, text):
        sid = SessionMemory.create_session()
        log_event(self.NAME, "SESSION_STARTED", {"session_id": sid})

        plan = self.planner.create_plan(text, sid)
        work = self.worker.execute_plan(text, plan, sid)
        evalr = self.evaluator.evaluate(text, plan, work, sid)

        return {"session_id": sid, "response": evalr["final_response"], "meta": {"score": evalr.get("score"), "level": evalr.get("level")}}

def run_agent(user_input: str):
    agent = MainAgent()
    result = agent.handle_message(user_input)
    return result["response"]
