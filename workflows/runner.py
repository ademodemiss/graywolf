import argparse
import json
import time
from pathlib import Path
import yaml # YAML desteği için eklendi

from policies.shell_policy import ShellPolicy
from tools.terminal_tool import TerminalTool


def load_workflow(path: str) -> dict:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Workflow file not found: {path}")

    if file_path.suffix.lower() == ".json":
        return json.loads(file_path.read_text(encoding="utf-8"))
    elif file_path.suffix.lower() in [".yaml", ".yml"]:
        return yaml.safe_load(file_path.read_text(encoding="utf-8"))

    raise ValueError("Şimdilik sadece JSON ve YAML workflow destekleniyor.")


def run_workflow(workflow: dict) -> dict:
    tool = TerminalTool(policy_engine=ShellPolicy(), log_dir="/home/adem/graywolf/logs")
    steps = workflow.get("steps", [])
    workflow_continue = bool(workflow.get("continue_on_error", False))
    results = []

    for step in steps:
        name = step.get("name", "unnamed")
        cmd = step.get("cmd", "")
        timeout = int(step.get("timeout", 60))
        continue_on_error = bool(step.get("continue_on_error", workflow_continue))
        max_retries = int(step.get("max_retries", 0))
        retry_delay_seconds = float(step.get("retry_delay_seconds", 1.0))

        if not cmd:
            results.append({"name": name, "status": "skipped", "reason": "missing cmd"})
            continue

        attempt = 0
        while attempt <= max_retries:
            result = tool.run_command(cmd, timeout=timeout)
            failed = result.get("status") in {"error", "timeout", "blocked", "needs_confirmation"}
            
            if not failed:
                break # Başarılı oldu, yeniden denemeye gerek yok

            # Eğer başarısız olduysa ve yeniden deneme hakkı varsa
            if attempt < max_retries:
                time.sleep(retry_delay_seconds * (2 ** attempt)) # Üstel backoff
            attempt += 1

        step_result = {
            "name": name,
            "cmd": cmd,
            "status": result.get("status"),
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
            "decision": result.get("log", {}).get("decision"),
            "exit_code": result.get("log", {}).get("exit_code"),
            "timeout": timeout,
            "continue_on_error": continue_on_error,
            "attempts": attempt # Kaç deneme yapıldığını kaydet
        }
        results.append(step_result)

        failed = step_result["status"] in {"error", "timeout", "blocked", "needs_confirmation"}
        if failed and not continue_on_error:
            return {
                "status": "stopped",
                "name": workflow.get("name", "unnamed"),
                "stopped_at": name,
                "reason": "step_failed",
                "results": results,
            }

    return {"status": "completed", "name": workflow.get("name", "unnamed"), "results": results}


def main():
    parser = argparse.ArgumentParser(description="GrayWolf workflow runner")
    parser.add_argument("--file", required=True, help="Workflow JSON file path")
    args = parser.parse_args()

    workflow = load_workflow(args.file)
    output = run_workflow(workflow)
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
