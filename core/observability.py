import datetime, json
def log_event(agent_name: str, event_type: str, payload=None):
    ts = datetime.datetime.utcnow().isoformat() + "Z"
    print("[LOG]", json.dumps({
        "timestamp": ts,
        "agent": agent_name,
        "event_type": event_type,
        "payload": payload or {}
    }))
