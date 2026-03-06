import argparse
import json
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def _run_command(cmd: str) -> dict:
    proc = subprocess.run(shlex.split(cmd), capture_output=True, text=True, check=False)
    return {
        "cmd": cmd,
        "exit_code": proc.returncode,
        "stdout": (proc.stdout or "").strip(),
        "stderr": (proc.stderr or "").strip(),
    }


def run_task(task_path: Path) -> dict:
    task = json.loads(task_path.read_text(encoding="utf-8"))
    results = []
    ok = True
    for cmd in task.get("verification_commands", []):
        r = _run_command(cmd)
        results.append(r)
        if r["exit_code"] != 0:
            ok = False

    out = {
        "status": "ok" if ok else "failed",
        "task_id": task.get("id"),
        "title": task.get("title"),
        "goal": task.get("goal"),
        "scope": task.get("scope", []),
        "verification": results,
        "ts": datetime.now(timezone.utc).isoformat(),
    }

    evidence_path = Path(f"/home/adem/graywolf/reports/task_{task.get('id','UNKNOWN')}_evidence.json")
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    out["artifact"] = str(evidence_path)
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", default="/home/adem/graywolf/tasks/examples/fix_semantic_search.json")
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()

    if args.test:
        result = run_task(Path(args.task))
    else:
        result = {"status": "idle"}

    print(json.dumps(result, ensure_ascii=False))
