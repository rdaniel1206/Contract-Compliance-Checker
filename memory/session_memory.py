"""Thread-safe session and working memory for the Contract Compliance Checker."""

import uuid
import threading
import datetime
from typing import Dict, Any, List, Optional

class SessionMemory:
    """In-memory thread-safe store for multi-agent state and audit trails."""
    _lock = threading.Lock()
    _sessions: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def create_session(cls, metadata: Optional[Dict[str, Any]] = None) -> str:
        with cls._lock:
            sid = str(uuid.uuid4())
            cls._sessions[sid] = {
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "metadata": metadata or {},
                "history": [],
                "data": {}
            }
            return sid

    @classmethod
    def set(cls, sid: str, key: str, value: Any) -> None:
        with cls._lock:
            if sid not in cls._sessions:
                cls._sessions[sid] = {
                    "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "metadata": {},
                    "history": [],
                    "data": {}
                }
            cls._sessions[sid]["data"][key] = value

    @classmethod
    def get(cls, sid: str, key: str, default: Any = None) -> Any:
        with cls._lock:
            session = cls._sessions.get(sid)
            if not session:
                return default
            return session.get("data", {}).get(key, default)

    @classmethod
    def append_history(cls, sid: str, entry: Dict[str, Any]) -> None:
        with cls._lock:
            if sid in cls._sessions:
                timestamped_entry = {
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    **entry
                }
                cls._sessions[sid]["history"].append(timestamped_entry)

    @classmethod
    def get_history(cls, sid: str) -> List[Dict[str, Any]]:
        with cls._lock:
            session = cls._sessions.get(sid)
            if not session:
                return []
            return list(session.get("history", []))

    @classmethod
    def get_session(cls, sid: str) -> Optional[Dict[str, Any]]:
        with cls._lock:
            return cls._sessions.get(sid)

    @classmethod
    def list_sessions(cls) -> List[str]:
        with cls._lock:
            return list(cls._sessions.keys())

    @classmethod
    def clear(cls) -> None:
        with cls._lock:
            cls._sessions.clear()
