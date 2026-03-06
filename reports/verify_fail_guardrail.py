import json
import subprocess
from pathlib import Path


def _run(args):
    p = subprocess.run(args, capture_output=True, text=True, check=False)
    payload = {}
    if p.stdout.strip():
        try:
            payload = json.loads(p.stdout.strip().splitlines()[-1])
        except Exception:
            payload = {"raw": p.stdout.strip()}
    return {
        "cmd": " ".join(args),
        "exit_code": p.returncode,
        "payload": payload,
        "stdout": (p.stdout or "").strip(),
        "stderr": (p.stderr or "").strip(),
    }


def run_report():
    base = "/home/adem/graywolf/tests/fixtures/tasks"

    verify_fail = _run([
        "python3", "-m", "core.git_task_commit", "--task", f"{base}/verify_fail_task.json"
    ])
    scope_violation = _run([
        "python3", "-m", "core.git_task_commit", "--task", "/home/adem/graywolf/tasks/examples/fix_semantic_search_scope_violation.json"
    ])
    no_changes = _run([
        "python3", "-m", "core.git_task_commit", "--task", f"{base}/no_changes_task.json"
    ])
    replay_mismatch = _run([
        "python3", "-m", "core.task_replay", "--test", "--task", f"{base}/replay_mismatch_task.json"
    ])

    checks = {
        "verify_fail_no_commit": verify_fail.get("payload", {}).get("decision") != "committed",
        "scope_violation_blocked": scope_violation.get("payload", {}).get("decision") == "blocked",
        "no_changes_no_commit": (
            no_changes.get("payload", {}).get("decision") != "committed"
            and no_changes.get("payload", {}).get("final_status") in {"no_changes", "scope_or_dirty_violation_blocked"}
        ),
        "replay_mismatch_flagged": replay_mismatch.get("payload", {}).get("diff_summary", {}).get("changed", 0) == 0,
    }

    out = {
        "status": "ok" if all(checks.values()) else "failed",
        "checks": checks,
        "scenarios": {
            "verify_fail": verify_fail,
            "scope_violation": scope_violation,
            "no_changes": no_changes,
            "replay_mismatch": replay_mismatch,
        },
    }

    out_path = Path("/home/adem/graywolf/reports/verify_fail_guardrail_report.json")
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    out["artifact"] = str(out_path)
    return out


if __name__ == "__main__":
    out = run_report()
    print(json.dumps(out, ensure_ascii=False))
    if out.get("status") != "ok":
        raise SystemExit(1)
