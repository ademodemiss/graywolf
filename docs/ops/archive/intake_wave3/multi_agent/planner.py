import json
from typing import Dict, Any, List

class Planner:
    def plan(self, goal: str, task_id: str, context: Dict = None) -> Dict[str, Any]:
        print(f"[Planner] Planning for: {goal}")
        plan_steps = []

        if "add two numbers" in goal.lower():
            main_file_path = f"tasks/code/{task_id}_main.py"
            test_file_path = f"tasks/code/{task_id}_tests.py"
            
            plan_steps.append({
                "action": "CREATE_FILE",
                "file_path": main_file_path,
                "content": "def add(a, b):\n    return a + b\n"
            })
            plan_steps.append({
                "action": "CREATE_FILE",
                "file_path": test_file_path,
                "content": f"import unittest\nfrom tasks.code.{task_id}_main import add\n\nclass TestAdd(unittest.TestCase):\n    def test_add_positive(self):\n        self.assertEqual(add(1, 2), 3)\n    def test_add_negative(self):\n        self.assertEqual(add(-1, -1), -2)\n    def test_add_zero(self):\n        self.assertEqual(add(0, 0), 0)\n"
            })
            plan_steps.append({
                "action": "RUN_COMMAND",
                "command": f"python3 -m unittest {test_file_path}",
                "expected_output_contains": "Ran 3 tests",
                "expected_exit_code": 0
            })
            plan_steps.append({
                "action": "REVIEW_FILE",
                "file_path": main_file_path,
                "criteria": "contains def add(a, b)"
            })
            plan_steps.append({
                "action": "REVIEW_FILE",
                "file_path": test_file_path,
                "criteria": "contains TestAdd(unittest.TestCase)"
            })
        else:
            plan_steps.append({"action": "GENERIC_TASK", "description": goal}) # Fallback for unknown goals

        return {"planner_id": "planner-001", "goal": goal, "context": context, "plan": plan_steps, "status": "planned"}

if __name__ == "__main__":
    planner = Planner()
    test_task_id = "TEST-PLAN-001"
    test_goal = "Implement a simple Python function to add two numbers."
    plan_output = planner.plan(test_goal, test_task_id)
    print(json.dumps(plan_output, indent=2))
    
    if len(plan_output["plan"]) > 0 and plan_output["plan"][0]["action"] == "CREATE_FILE": 
        print("Planner Smoke Test PASSED ✅")
    else: 
        print("Planner Smoke Test FAILED ❌")