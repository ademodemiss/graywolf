import datetime


def heartbeat_payload(node_id: str = "node-local", status: str = "running", active_tasks: int = 0) -> dict:
    return {
        "node_id": node_id,
        "status": status,
        "active_tasks": active_tasks,
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
