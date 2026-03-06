import json
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional

class HumanGate:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def request_approval(self, task_id: str, risk_level: str, approver: str = "admin") -> Dict[str, Any]:
        request_id = f"GATE-{task_id}-{int(time.time())}"
        request_data = {
            "request_id": request_id,
            "task_id": task_id,
            "risk_level": risk_level,
            "approver": approver,
            "status": "pending",
            "timestamp": datetime.now().isoformat()
        }

        # In a real system, this would send a notification (e.g., Telegram) and wait.
        # For simulation/automation purposes, we might auto-approve low risk or wait for a signal file.
        
        # Simulated logic:
        if risk_level == "low":
            request_data["status"] = "auto_approved"
            request_data["comment"] = "Low risk auto-approved"
        else:
            # High risk requires manual intervention simulation
            # We'll check for an override flag for testing purposes
            if os.environ.get("GRAYWOLF_AUTO_APPROVE") == "true":
                 request_data["status"] = "approved"
                 request_data["comment"] = "Auto-approved via ENV override"
            else:
                 request_data["status"] = "denied"
                 request_data["comment"] = "High risk requires explicit approval (simulation denied)"

        # Log the gate decision
        gate_log_path = os.path.join(self.output_dir, f"gate_decision_{task_id}.json")
        with open(gate_log_path, "w") as f:
            json.dump(request_data, f, indent=2)
            
        return request_data

if __name__ == "__main__":
    # Smoke Test for Phase 247
    print("Starting HumanGate Smoke Test...")
    
    gate = HumanGate()
    
    # Test 1: Low Risk Auto-Approve
    result_low = gate.request_approval("TASK-SMOKE-247-LOW", "low")
    print(f"Low Risk Result: {result_low['status']}")
    
    # Test 2: High Risk Deny (Default)
    result_high = gate.request_approval("TASK-SMOKE-247-HIGH", "high")
    print(f"High Risk Result: {result_high['status']}")
    
    # Test 3: High Risk Approve (with ENV)
    os.environ["GRAYWOLF_AUTO_APPROVE"] = "true"
    result_override = gate.request_approval("TASK-SMOKE-247-OVERRIDE", "high")
    print(f"Override Result: {result_override['status']}")
    
    # Verify
    if (result_low["status"] == "auto_approved" and 
        result_high["status"] == "denied" and 
        result_override["status"] == "approved"):
        print("Smoke Test PASSED ✅")
        
        # Generate official report
        report = {
            "phase": 247,
            "status": "completed",
            "module": "core/human_gate.py",
            "gate_samples": [result_low, result_high, result_override],
            "timestamp": datetime.now().isoformat()
        }
        with open("reports/human_approval_gate_report.json", "w") as f:
            json.dump(report, f, indent=2)
    else:
        print("Smoke Test FAILED ❌")
        exit(1)
