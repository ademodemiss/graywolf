import argparse
import datetime
import json
import shlex
import subprocess
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait

from core.event_bus import EventBus
from core.event_types import EventTypes

BUS = EventBus()


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _run_step(step: dict) -> dict:
    cmd = step.get("run", "")
    started_at = _now_iso()
    p = subprocess.run(shlex.split(cmd), capture_output=True, text=True, check=False)
    finished_at = _now_iso()
    return {
        "id": step["id"],
        "run": cmd,
        "started_at": started_at,
        "finished_at": finished_at,
        "exit_code": p.returncode,
        "stdout": (p.stdout or "").strip(),
        "stderr": (p.stderr or "").strip(),
    }


def execute_dag(workflow: dict, max_workers: int = 4) -> dict:
    BUS.publish(EventTypes.WORKFLOW_STARTED, {'step_count': len(workflow.get('steps', []))})
    steps = workflow.get("steps", [])
    step_map = {s["id"]: s for s in steps}
    deps = {s["id"]: set(s.get("needs", [])) for s in steps}

    completed = set()
    submitted = set()
    running = {}
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        while len(completed) < len(steps):
            ready = [sid for sid, need in deps.items() if sid not in submitted and need.issubset(completed)]
            for sid in ready:
                fut = ex.submit(_run_step, step_map[sid])
                running[fut] = sid
                submitted.add(sid)

            if not running:
                BUS.publish(EventTypes.WORKFLOW_COMPLETED, {'status': 'error'})
                return {"status": "error", "error": "deadlock_or_invalid_dependencies", "completed": list(completed)}

            done, _ = wait(running.keys(), return_when=FIRST_COMPLETED)
            for fut in done:
                sid = running.pop(fut)
                out = fut.result()
                results.append(out)
                if out["exit_code"] == 0:
                    completed.add(sid)
                else:
                    BUS.publish(EventTypes.WORKFLOW_COMPLETED, {'status': 'failed', 'failed_step': sid})
                    return {"status": "failed", "failed_step": sid, "results": results}

    BUS.publish(EventTypes.WORKFLOW_COMPLETED, {'status': 'completed'})
    return {"status": "completed", "results": results}


def _ts(s: str):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))


def run_test() -> dict:
    # A -> (B,C) -> D
    wf = {
        "steps": [
            {"id": "A", "run": "python3 -c \"import time; time.sleep(0.4); print('A')\"", "needs": []},
            {"id": "B", "run": "python3 -c \"import time; time.sleep(1.0); print('B')\"", "needs": ["A"]},
            {"id": "C", "run": "python3 -c \"import time; time.sleep(1.0); print('C')\"", "needs": ["A"]},
            {"id": "D", "run": "python3 -c \"print('D')\"", "needs": ["B", "C"]},
        ]
    }
    out = execute_dag(wf, max_workers=4)
    if out.get("status") != "completed":
        return {"status": "failed", "detail": out}

    by = {r["id"]: r for r in out["results"]}
    a_done = _ts(by["A"]["finished_at"])
    b_start = _ts(by["B"]["started_at"])
    c_start = _ts(by["C"]["started_at"])
    b_done = _ts(by["B"]["finished_at"])
    c_done = _ts(by["C"]["finished_at"])
    d_start = _ts(by["D"]["started_at"])

    parallel_bc = abs((b_start - c_start).total_seconds()) < 0.3
    d_after_bc = d_start >= b_done and d_start >= c_done
    a_before_bc = b_start >= a_done and c_start >= a_done

    return {
        "status": "ok" if (parallel_bc and d_after_bc and a_before_bc) else "failed",
        "checks": {"a_before_bc": a_before_bc, "parallel_bc": parallel_bc, "d_after_bc": d_after_bc},
        "results": out["results"],
    }


def main():
    p = argparse.ArgumentParser(description="GrayWolf DAG Executor")
    p.add_argument("--test", action="store_true")
    args = p.parse_args()

    if args.test:
        print(json.dumps(run_test(), ensure_ascii=False))
        return

    print(json.dumps({"status": "idle"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
