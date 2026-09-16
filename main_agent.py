"""Main Agent Orchestrator for the Contract Compliance Checker."""

import os
import sys
from typing import Dict, Any, Optional

# Ensure current directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from agents.planner import Planner
from agents.worker import Worker
from agents.evaluator import Evaluator
from memory.session_memory import SessionMemory
from core.observability import log_event
from core import a2a_protocol as protocol
from tools.tools import load_contract_file

class MainAgent:
    """Master orchestrator managing A2A protocol coordination across specialized agents."""
    NAME = "main_agent"

    def __init__(self):
        self.planner = Planner()
        self.worker = Worker()
        self.evaluator = Evaluator()

    def handle_message(self, contract_input: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Runs the complete multi-agent compliance pipeline on given contract text."""
        # 1. Initialize session memory
        sid = SessionMemory.create_session(metadata=metadata)
        log_event(self.NAME, "SESSION_STARTED", {"session_id": sid, "metadata": metadata or {}}, session_id=sid)
        SessionMemory.set(sid, "raw_input", contract_input)

        # 2. Planner Agent Step via A2A Protocol
        plan_req = protocol.make_plan_request(sid, contract_input, metadata)
        SessionMemory.append_history(sid, {"type": "A2A_OUT", "message": plan_req})
        plan_res = self.planner.handle_a2a_message(plan_req)
        SessionMemory.append_history(sid, {"type": "A2A_IN", "message": plan_res})
        plan = plan_res["payload"]["plan"]
        SessionMemory.set(sid, "plan", plan)

        # 3. Worker Agent Step via A2A Protocol
        work_req = protocol.make_work_request(sid, plan, contract_input)
        SessionMemory.append_history(sid, {"type": "A2A_OUT", "message": work_req})
        work_res = self.worker.handle_a2a_message(work_req)
        SessionMemory.append_history(sid, {"type": "A2A_IN", "message": work_res})
        work_result = work_res["payload"]["work_result"]
        SessionMemory.set(sid, "work_result", work_result)

        # 4. Evaluator Agent Step via A2A Protocol
        eval_req = protocol.make_eval_request(sid, plan, work_result, contract_input)
        SessionMemory.append_history(sid, {"type": "A2A_OUT", "message": eval_req})
        eval_res = self.evaluator.handle_a2a_message(eval_req)
        SessionMemory.append_history(sid, {"type": "A2A_IN", "message": eval_res})
        eval_result = eval_res["payload"]["evaluation_result"]
        SessionMemory.set(sid, "evaluation_result", eval_result)

        log_event(self.NAME, "SESSION_COMPLETED", {
            "session_id": sid,
            "contract_type": eval_result.get("contract_type"),
            "risk_level": eval_result.get("level"),
            "score": eval_result.get("score")
        }, session_id=sid)

        return {
            "session_id": sid,
            "contract_type": eval_result.get("contract_type"),
            "response": eval_result.get("final_response"),
            "markdown_report": eval_result.get("markdown_report"),
            "report_data": eval_result.get("report_data"),
            "meta": {
                "score": eval_result.get("score"),
                "level": eval_result.get("level"),
                "red_flags": eval_result.get("red_flags", [])
            }
        }

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyzes a contract from a file path."""
        text, error = load_contract_file(file_path)
        if error and not text:
            return {
                "session_id": "",
                "error": error,
                "response": f"Failed to load file: {error}"
            }
        
        metadata = {"file_path": file_path, "filename": os.path.basename(file_path)}
        result = self.handle_message(text, metadata=metadata)
        if error:
            result["warning"] = error
        return result

def run_agent(user_input_or_filepath: str) -> str:
    """Convenience entry point for CLI and external callers."""
    agent = MainAgent()
    # Check if input is an existing file path
    if os.path.isfile(user_input_or_filepath):
        result = agent.analyze_file(user_input_or_filepath)
    else:
        result = agent.handle_message(user_input_or_filepath)
    return result.get("response", "No response generated.")

