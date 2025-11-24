from typing import Dict, Any
import uuid, threading

class SessionMemory:
    _lock = threading.Lock()
    _sessions: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def create_session(cls) -> str:
        with cls._lock:
            sid = str(uuid.uuid4())
            cls._sessions[sid] = {}
            return sid

    @classmethod
    def set(cls, sid: str, key: str, value: Any) -> None:
        with cls._lock:
            cls._sessions.setdefault(sid, {})[key] = value

    @classmethod
    def get(cls, sid: str, key: str, default=None) -> Any:
        with cls._lock:
            return cls._sessions.get(sid, {}).get(key, default)
