import json
from reports.verify_fail_guardrail import run_report


def run_test():
    out = run_report()
    return {
        "status": out.get("status", "failed"),
        "artifact": out.get("artifact"),
        "checks": out.get("checks", {}),
    }


if __name__ == "__main__":
    out = run_test()
    print(json.dumps(out, ensure_ascii=False))
    if out.get("status") != "ok":
        raise SystemExit(1)
