import json
import os
from typing import Dict, Any, List
import sys

sys.path.append('/home/adem/.openclaw/workspace')

# Dynamically import default_api from the global context
# This assumes default_api is available in the OpenClaw execution environment
try:
    from openclaw_api import default_api
except ImportError:
    # Fallback for local testing or different environments
    print("Warning: openclaw_api.default_api not found. Using a mock default_api.")
    class MockDefaultApi:
        def write(self, path: str, content: str):
            print(f"Mocking write to {path} with content:\n{content[:100]}...")
            # Simulate file creation for testing purposes
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            return {"write_response": {"output": f"Successfully wrote {len(content)} bytes to {path}"}}
        def exec(self, command: str, workdir: str = None):
            print(f"Mocking exec: {command}")
            # Simulate command execution
            if "python3 -m unittest" in command:
                return {"exec_response": {"output": "Ran 3 tests in 0.001s\n\nOK", "exit_code": 0}}
            return {"exec_response": {"output": "Mock command output", "exit_code": 0}}

    default_api = MockDefaultApi()


class Coder:
    def code(self, plan_steps: List[Dict[str, Any]], task_id: str, context: Dict = None) -> Dict[str, Any]:
        print(f"[Coder] Coding for task {task_id} with plan: {plan_steps}")
        code_artifacts = []
        status = "coded"

        for step in plan_steps:
            action = step.get("action")
            
            if action == "CREATE_FILE":
                file_path = f"/home/adem/graywolf/{step["file_path"]}" # Ensure absolute path
                content = step["content"]
                print(f"[Coder] Creating file: {file_path}")
                try:
                    write_result = default_api.write(path=file_path, content=content)
                    if "error" in write_result:
                        status = "failed"
                        print(f"[Coder ERROR] Failed to create file {file_path}: {write_result['error']}")
                        break
                    code_artifacts.append(file_path)
                except Exception as e:
                    status = "failed"
                    print(f"[Coder ERROR] Exception creating file {file_path}: {e}")
                    break
            # Add more actions like MODIFY_FILE if needed in the future
            elif action == "RUN_COMMAND":
                # Coder might compile or run initial checks
                command = step["command"]
                print(f"[Coder] Running command: {command}")
                try:
                    exec_result = default_api.exec(command=command, workdir="/home/adem/graywolf/")
                    if exec_result.get("exec_response", {}).get("exit_code") != 0:
                        status = "failed"
                        print(f"[Coder ERROR] Command failed: {command}, Output: {exec_result}")
                        break
                except Exception as e:
                    status = "failed"
                    print(f"[Coder ERROR] Exception running command {command}: {e}")
                    break
            
            # Other actions are not handled by Coder, but passed through.

        return {"coder_id": "coder-001", "task_id": task_id, "plan_executed": plan_steps, "code_artifacts": code_artifacts, "status": status, "context": context}

if __name__ == "__main__":
    coder = Coder()
    test_task_id = "TASK-C-002"
    test_plan = [
        {"action": "CREATE_FILE", "file_path": f"tasks/code/{test_task_id}_main.py", "content": "def subtract(a, b):\n    return a - b\n"},
        {"action": "CREATE_FILE", "file_path": f"tasks/code/{test_task_id}_tests.py", "content": f"import unittest\nfrom tasks.code.{test_task_id}_main import subtract\nclass TestSubtract(unittest.TestCase):\n    def test_subtract_positive(self):\n        self.assertEqual(subtract(5, 2), 3)\n"},
        {"action": "RUN_COMMAND", "command": f"python3 -m unittest /home/adem/graywolf/tasks/code/{test_task_id}_tests.py", "expected_exit_code": 0}
    ]
    code_output = coder.code(test_plan, test_task_id)
    print(json.dumps(code_output, indent=2))

    if code_output["status"] == "coded" and len(code_output["code_artifacts"]) == 2:
        print("Coder Smoke Test PASSED ✅")
    else:
        print("Coder Smoke Test FAILED ❌")
