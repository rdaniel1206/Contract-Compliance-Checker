"""Agent-to-Agent (A2A) Protocol for structured message exchange between agents."""

import uuid
import datetime
from typing import Dict, Any, Optional

def create_message(
    sender: str,
    receiver: str,
    message_type: str,
    payload: Dict[str, Any],
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """Constructs a standardized A2A message packet."""
    return {
        "message_id": str(uuid.uuid4()),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "sender": sender,
        "receiver": receiver,
        "message_type": message_type,
        "session_id": session_id or payload.get("session_id", ""),
        "payload": payload
    }

def make_plan_request(sid: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return create_message(
        sender="main_agent",
        receiver="planner",
        message_type="PLAN_REQUEST",
        payload={"session_id": sid, "contract_text": text, "metadata": metadata or {}},
        session_id=sid
    )

def make_plan_response(sid: str, plan: Dict[str, Any]) -> Dict[str, Any]:
    return create_message(
        sender="planner",
        receiver="main_agent",
        message_type="PLAN_RESPONSE",
        payload={"session_id": sid, "plan": plan},
        session_id=sid
    )

def make_work_request(sid: str, plan: Dict[str, Any], text: str) -> Dict[str, Any]:
    return create_message(
        sender="main_agent",
        receiver="worker",
        message_type="WORK_REQUEST",
        payload={"session_id": sid, "plan": plan, "contract_text": text},
        session_id=sid
    )

def make_work_response(sid: str, work_result: Dict[str, Any]) -> Dict[str, Any]:
    return create_message(
        sender="worker",
        receiver="main_agent",
        message_type="WORK_RESPONSE",
        payload={"session_id": sid, "work_result": work_result},
        session_id=sid
    )

def make_eval_request(sid: str, plan: Dict[str, Any], work_result: Dict[str, Any], text: str) -> Dict[str, Any]:
    return create_message(
        sender="main_agent",
        receiver="evaluator",
        message_type="EVAL_REQUEST",
        payload={"session_id": sid, "plan": plan, "work_result": work_result, "contract_text": text},
        session_id=sid
    )

def make_eval_response(sid: str, evaluation_result: Dict[str, Any]) -> Dict[str, Any]:
    return create_message(
        sender="evaluator",
        receiver="main_agent",
        message_type="EVAL_RESPONSE",
        payload={"session_id": sid, "evaluation_result": evaluation_result},
        session_id=sid
    )
