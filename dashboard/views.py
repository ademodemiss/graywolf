from dashboard.data import build_status_payload


def index_context() -> dict:
    return {"initial_status": build_status_payload()}
