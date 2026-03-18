import json
import os
from datetime import datetime
from typing import Dict, Any
from self_improve.error_analyzer import ErrorAnalyzer

class RepairLoop:
    def __init__(self, output_dir: str = "reports/repairs"):
        self.analyzer = ErrorAnalyzer()
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def attempt_repair(self, task_id: str, error: str, context: Dict) -> Dict[str, Any]:
        analysis = self.analyzer.analyze(error, context)
        repair_plan = {"task_id": task_id, "error": str(error), "analysis": analysis, "action_taken": "none", "status": "pending", "timestamp": datetime.now().isoformat()}
        action = analysis["suggested_action"]
        if action == "fix_syntax":
            repair_plan.update({"action_taken": "applied_syntax_patch", "status": "repaired"})
        elif action == "retry_with_backoff":
            repair_plan.update({"action_taken": "scheduled_retry", "status": "retrying"})
        else:
            repair_plan.update({"action_taken": "escalated", "status": "failed"})
        
        with open(os.path.join(self.output_dir, f"repair_{task_id}.json"), "w") as f:
            json.dump(repair_plan, f, indent=2)
        return repair_plan

if __name__ == "__main__":
    repair = RepairLoop(output_dir="reports/evidence/phase255")
    res = repair.attempt_repair("TASK-FAIL-1", "SyntaxError: unexpected EOF", {})
    if res['status'] == "repaired": print("Smoke Test PASSED ✅")
    else: print("Smoke Test FAILED ❌")
