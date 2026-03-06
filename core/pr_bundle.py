import json
import os
from datetime import datetime
from typing import Dict, Any, List

class PRBundleGenerator:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_bundle(self, task_id: str, summary: str, risks: List[str], verify_steps: List[str], evidence_path: str) -> Dict[str, Any]:
        # Load evidence if exists
        evidence_data = {}
        if os.path.exists(evidence_path):
            with open(evidence_path, "r") as f:
                evidence_data = json.load(f)
        else:
            evidence_data = {"error": "Evidence file missing"}

        bundle = {
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "risks": risks,
            "verification": {
                "steps": verify_steps,
                "status": "pending_review"
            },
            "evidence_snapshot": evidence_data
        }

        bundle_path = os.path.join(self.output_dir, f"pr_bundle_{task_id}.json")
        with open(bundle_path, "w") as f:
            json.dump(bundle, f, indent=2)
        
        return bundle

if __name__ == "__main__":
    # Smoke Test for Phase 246
    print("Starting PRBundleGenerator Smoke Test...")
    
    # Create dummy evidence
    dummy_evidence = "reports/dummy_pr_evidence.json"
    with open(dummy_evidence, "w") as f:
        json.dump({"test_run": "success", "coverage": 95}, f)
        
    generator = PRBundleGenerator()
    result = generator.generate_bundle(
        task_id="TASK-SMOKE-246",
        summary="Implemented PR Bundle Generator for Phase 246",
        risks=["None identified", "Low complexity"],
        verify_steps=["Run smoke test", "Check JSON output"],
        evidence_path=dummy_evidence
    )
    
    print(f"Bundle Result: {json.dumps(result, indent=2)}")
    
    # Verify
    if result["task_id"] == "TASK-SMOKE-246" and "test_run" in result["evidence_snapshot"]:
        print("Smoke Test PASSED ✅")
        
        # Generate official report
        report = {
            "phase": 246,
            "status": "completed",
            "module": "core/pr_bundle.py",
            "bundle_sample": result,
            "timestamp": datetime.now().isoformat()
        }
        with open("reports/pr_bundle_report.json", "w") as f:
            json.dump(report, f, indent=2)
    else:
        print("Smoke Test FAILED ❌")
        exit(1)
