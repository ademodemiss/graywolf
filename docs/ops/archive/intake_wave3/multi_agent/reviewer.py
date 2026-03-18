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
        def read(self, path: str):
            print(f"Mocking read from {path}")
            if "main.py" in path:
                return {"read_response": {"output": "def add(a, b):\n    return a + b\n"}}
            if "tests.py" in path:
                return {"read_response": {"output": "import unittest\nfrom tasks.code.TASK-COORD-001_main import add\nclass TestAdd(unittest.TestCase):\n    def test_add_positive(self):\n        self.assertEqual(add(1, 2), 3)\n"}}
            return {"read_response": {"output": ""}}
        def write(self, path: str, content: str):
            print(f"Mocking write to {path}")
            return {"write_response": {"output": f"Successfully wrote {len(content)} bytes to {path}"}}
    default_api = MockDefaultApi()

class Reviewer:
    def review(self, plan_steps: List[Dict[str, Any]], task_id: str, context: Dict = None) -> Dict[str, Any]:
        print(f"[Reviewer] Reviewing for task {task_id} with plan: {plan_steps}")
        review_comments = []
        status = "approved"

        for step in plan_steps:
            action = step.get("action")
            
            if action == "REVIEW_FILE":
                file_path = f"/home/adem/graywolf/{step["file_path"]}" # Ensure absolute path
                criteria = step["criteria"]
                print(f"[Reviewer] Reviewing file: {file_path} with criteria: {criteria}")
                try:
                    read_result = default_api.read(path=file_path)
                    if "error" in read_result:
                        status = "needs_rework"
                        review_comments.append(f"Failed to read file {file_path}: {read_result['error']}")
                        break
                    
                    file_content = read_result.get("read_response", {}).get("output", "")
                    
                    if "contains" in criteria:
                        keyword = criteria.split("contains ")[1]
                        keyword = keyword.strip().replace("'", "").replace('"', '')
                        if keyword not in file_content:
                            status = "needs_rework"
                            review_comments.append(f"File {file_path} does not contain required keyword: '{keyword}'")

                except Exception as e:
                    status = "needs_rework"
                    review_comments.append(f"Exception reviewing file {file_path}: {e}")
                    break
            # Other actions are not handled by Reviewer, but passed through.

        return {"reviewer_id": "reviewer-001", "task_id": task_id, "plan_reviewed": plan_steps, "comments": review_comments, "status": status}

if __name__ == "__main__":
    reviewer = Reviewer()
    test_task_id = "TASK-REV-001"

    # Create dummy files for testing
    os.makedirs(f"/home/adem/graywolf/tasks/code/", exist_ok=True)
    with open(f"/home/adem/graywolf/tasks/code/{test_task_id}_main.py", "w") as f:
        f.write("def multiply(a, b):\n    return a * b\n")
    with open(f"/home/adem/graywolf/tasks/code/{test_task_id}_tests.py", "w") as f:
        f.write("import unittest\nfrom tasks.code.TASK-REV-001_main import multiply\nclass TestMultiply(unittest.TestCase):\n    def test_multiply_positive(self):\n        self.assertEqual(multiply(1, 2), 2)\n")

    test_plan = [
        {"action": "REVIEW_FILE", "file_path": f"tasks/code/{test_task_id}_main.py", "criteria": "contains 'def multiply'"},
        {"action": "REVIEW_FILE", "file_path": f"tasks/code/{test_task_id}_tests.py", "criteria": "contains 'TestMultiply'"},
        {"action": "REVIEW_FILE", "file_path": f"tasks/code/{test_task_id}_main.py", "criteria": "contains 'TODO'"} # This should cause needs_rework
    ]
    review_output = reviewer.review(test_plan, test_task_id)
    print(json.dumps(review_output, indent=2))

    if review_output["status"] == "needs_rework" and len(review_output["comments"]) > 0:
        print("Reviewer Smoke Test PASSED ✅ (expected needs_rework)")
    else:
        print("Reviewer Smoke Test FAILED ❌")
