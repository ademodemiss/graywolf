import json
import os
from typing import Dict, Any, List
import sys

sys.path.append('/home/adem/.openclaw/workspace')

# Dynamically import default_api from the global context
try:
    from openclaw_api import default_api
except ImportError:
    print("Warning: openclaw_api.default_api not found. Using a mock default_api.")
    class MockDefaultApi:
        def exec(self, command: str, workdir: str = None):
            print(f"Mocking exec: {command}")
            if "python3 -m unittest" in command:
                if "fail" in command:
                    return {"exec_response": {"output": "Ran 1 test in 0.001s\nFAIL", "exit_code": 1}}
                return {"exec_response": {"output": "Ran 2 tests in 0.001s\n\nOK", "exit_code": 0}}
            return {"exec_response": {"output": "Mock command output", "exit_code": 0}}
        def write(self, path: str, content: str):
            print(f"Mocking write to {path}")
            return {"write_response": {"output": f"Successfully wrote {len(content)} bytes to {path}"}}
    default_api = MockDefaultApi()

class Tester:
    def test(self, plan_steps: List[Dict[str, Any]], task_id: str, context: Dict = None) -> Dict[str, Any]:
        print(f"[Tester] Testing for task {task_id} with plan: {plan_steps}")
        test_results = []
        overall_status = "passed"

        for step in plan_steps:
            action = step.get("action")
            
            if action == "RUN_COMMAND":
                command = step["command"]
                expected_output_contains = step.get("expected_output_contains", "")
                expected_exit_code = step.get("expected_exit_code", 0)
                print(f"[Tester] Running command: {command}")
                try:
                    exec_result = default_api.exec(command=command, workdir="/home/adem/graywolf/")
                    stdout = exec_result.get("exec_response", {}).get("output", "")
                    exit_code = exec_result.get("exec_response", {}).get("exit_code")

                    test_status = "passed"
                    test_comments = []

                    if exit_code != expected_exit_code:
                        test_status = "failed"
                        test_comments.append(f"Command exited with code {exit_code}, expected {expected_exit_code}.")
                    
                    if expected_output_contains and expected_output_contains not in stdout:
                        test_status = "failed"
                        test_comments.append(f"Command output did not contain expected string: '{expected_output_contains}'")
                    
                    test_results.append({
                        "command": command,
                        "stdout": stdout,
                        "exit_code": exit_code,
                        "status": test_status,
                        "comments": test_comments
                    })
                    
                    if test_status == "failed":
                        overall_status = "failed"
                        # No break here, run all tests to collect all results

                except Exception as e:
                    overall_status = "failed"
                    test_results.append({"command": command, "status": "error", "comments": [f"Exception running command: {e}"]})
                    # No break here, run all tests to collect all results

            # Other actions are not handled by Tester, but passed through.

        return {"tester_id": "tester-001", "task_id": task_id, "plan_tested": plan_steps, "test_results": test_results, "overall_status": overall_status}

if __name__ == "__main__":
    tester = Tester()
    test_task_id = "TASK-TEST-001"

    # Create dummy files for testing (if needed by the command)
    os.makedirs(f"/home/adem/graywolf/tasks/code/", exist_ok=True)
    with open(f"/home/adem/graywolf/tasks/code/{test_task_id}_main.py", "w") as f:
        f.write("def divide(a, b):\n    return a / b\n")
    with open(f"/home/adem/graywolf/tasks/code/{test_task_id}_tests.py", "w") as f:
        f.write("import unittest\nfrom tasks.code.TASK-TEST-001_main import divide\nclass TestDivide(unittest.TestCase):\n    def test_divide_positive(self):\n        self.assertEqual(divide(4, 2), 2)\n    def test_divide_by_zero(self):\n        with self.assertRaises(ZeroDivisionError):\n            divide(1, 0)\n")

    test_plan = [
        {"action": "RUN_COMMAND", "command": f"python3 -m unittest /home/adem/graywolf/tasks/code/{test_task_id}_tests.py", "expected_output_contains": "Ran 2 tests", "expected_exit_code": 0}
    ]
    test_output = tester.test(test_plan, test_task_id)
    print(json.dumps(test_output, indent=2))

    if test_output["overall_status"] == "passed":
        print("Tester Smoke Test PASSED ✅")
    else:
        print("Tester Smoke Test FAILED ❌")
