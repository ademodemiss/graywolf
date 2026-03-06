import json
import os
from datetime import datetime
from typing import Dict, Any, List

class ProdChecklist:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Standard Checklist Items
        self.checklist = [
            "tests_passed",
            "coverage_threshold_met",
            "security_scan_clean",
            "performance_metrics_ok",
            "documentation_updated",
            "rollback_plan_verified"
        ]

    def run_check(self, task_id: str, results: Dict[str, bool]) -> Dict[str, Any]:
        report = {
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "ready": True,
            "missing": []
        }

        for item in self.checklist:
            status = results.get(item, False)
            report["checks"][item] = status
            if not status:
                report["ready"] = False
                report["missing"].append(item)
        
        # Persist report
        report_path = os.path.join(self.output_dir, f"readiness_check_{task_id}.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
            
        return report

if __name__ == "__main__":
    # Smoke Test for Phase 248
    print("Starting ProdChecklist Smoke Test...")
    
    checker = ProdChecklist()
    
    # Test 1: Fail Case (Missing items)
    results_fail = {
        "tests_passed": True,
        "coverage_threshold_met": False,
        "security_scan_clean": True
    }
    check_fail = checker.run_check("TASK-SMOKE-248-FAIL", results_fail)
    print(f"Fail Case Ready: {check_fail['ready']} (Missing: {check_fail['missing']})")
    
    # Test 2: Pass Case (All items True)
    results_pass = {
        "tests_passed": True,
        "coverage_threshold_met": True,
        "security_scan_clean": True,
        "performance_metrics_ok": True,
        "documentation_updated": True,
        "rollback_plan_verified": True
    }
    check_pass = checker.run_check("TASK-SMOKE-248-PASS", results_pass)
    print(f"Pass Case Ready: {check_pass['ready']}")
    
    # Verify
    if not check_fail["ready"] and check_pass["ready"]:
        print("Smoke Test PASSED ✅")
        
        # Generate official report
        report = {
            "phase": 248,
            "status": "completed",
            "module": "core/prod_checklist.py",
            "check_samples": [check_fail, check_pass],
            "timestamp": datetime.now().isoformat()
        }
        with open("reports/production_readiness_report.json", "w") as f:
            json.dump(report, f, indent=2)
    else:
        print("Smoke Test FAILED ❌")
        exit(1)
