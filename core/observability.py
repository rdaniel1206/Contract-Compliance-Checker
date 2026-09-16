"""Structured observability and event logging for multi-agent workflows."""

import datetime
import json
from typing import Dict, Any, Optional, List, Callable

_LOG_HISTORY: List[Dict[str, Any]] = []
_SUBSCRIBERS: List[Callable[[Dict[str, Any]], None]] = []

def subscribe_to_logs(callback: Callable[[Dict[str, Any]], None]) -> None:
    """Subscribe a callback to receive live log events."""
    if callback not in _SUBSCRIBERS:
        _SUBSCRIBERS.append(callback)

def unsubscribe_from_logs(callback: Callable[[Dict[str, Any]], None]) -> None:
    """Unsubscribe a callback."""
    if callback in _SUBSCRIBERS:
        _SUBSCRIBERS.remove(callback)

def log_event(
    agent_name: str,
    event_type: str,
    payload: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None,
    print_log: bool = False
) -> Dict[str, Any]:
    """Records an observability log event."""
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    record = {
        "timestamp": ts,
        "agent": agent_name,
        "event_type": event_type,
        "session_id": session_id or (payload.get("session_id") if isinstance(payload, dict) else None),
        "payload": payload or {}
    }
    _LOG_HISTORY.append(record)

    if print_log:
        print(f"[LOG][{agent_name}][{event_type}] {json.dumps(record['payload'], default=str)}")

    for subscriber in list(_SUBSCRIBERS):
        try:
            subscriber(record)
        except Exception:
            pass

    return record

def get_event_logs(session_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves logged events, optionally filtered by session_id."""
    if session_id:
        return [log for log in _LOG_HISTORY if log.get("session_id") == session_id]
    return list(_LOG_HISTORY)

def clear_logs() -> None:
    """Clears log history."""
    _LOG_HISTORY.clear()

