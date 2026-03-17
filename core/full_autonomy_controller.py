import json
import os
import time
from datetime import datetime
from typing import Dict, Any

# Core Imports
from core.autonomous_loop import AutonomousLoop
from dashboard.dashboard_generator import DashboardGenerator

class FullAutonomyController:
    def __init__(self, workspace_dir: str = "."):
        self.workspace_dir = workspace_dir
        self.loop = AutonomousLoop(queue_dir="tasks/queue", processed_dir="tasks/processed")
        self.dashboard = DashboardGenerator(output_dir="reports/dashboard")
        self.run_report_dir = "reports/autonomy_runs"
        os.makedirs(self.run_report_dir, exist_ok=True)

    def run_cycle(self, max_tasks: int = 1) -> Dict[str, Any]:
        run_id = f"RUN-{int(datetime.now().timestamp())}"
        report = {
            "run_id": run_id,
            "status": "started",
            "timestamp": datetime.now().isoformat(),
            "tasks_processed": []
        }

        print(f"[Autonomy] Starting Cycle {run_id} (Max Tasks: {max_tasks})")
        
        count = 0
        while count < max_tasks:
            # 1. Run Autonomous Loop Step
            result = self.loop.run_once()
            
            if result["status"] == "idle":
                print("[Autonomy] Queue empty. Stopping cycle.")
                break
            
            report["tasks_processed"].append(result)
            count += 1
            
            # 2. Update Dashboard
            self.dashboard.generate_snapshot()
            
            # Safety break for simulation
            if result["status"] == "error":
                print("[Autonomy] Critical error encountered. Halting.")
                report["status"] = "halted_on_error"
                break

        if report["status"] == "started":
            report["status"] = "completed"
            
        # Save Run Report
        path = os.path.join(self.run_report_dir, f"autonomy_report_{run_id}.json")
        with open(path, "w") as f:
            json.dump(report, f, indent=2)
            
        return report

if __name__ == "__main__":
    # Smoke Test
    print("Starting Full Autonomy Smoke Test...")
    
    # Ensure queue has a task (using Mock LLM in AutonomousLoop via environment variable or direct injection if needed)
    # Since AutonomousLoop uses MockLLM in its main block but here we import it, we need to ensure it has an LLM or mocking works.
    # For this smoke test, we rely on AutonomousLoop's internal handling or we need to inject a mock.
    
    # Let's inject a Mock LLM into the loop instance
    class MockLLM:
        def generate_response(self, prompt, **kwargs): return "step1|echo 'Autonomy Test'"
        def get_model_info(self): return {"name": "mock_autonomy"}
        def stream_response(self, prompt, **kwargs): yield "step1|echo 'Autonomy Test'"
        def chat_completion(self, messages, **kwargs): return "step1|echo 'Autonomy Test'"

    # Import Orchestrator here to instantiate
    from core.orchestrator import Orchestrator
    controller = FullAutonomyController()
    controller.loop.llm = MockLLM()
    controller.loop.orchestrator = Orchestrator(controller.loop.llm)
    
    # Seed a small queue for deterministic smoke test
    controller.loop.queue.add_task({"task_id": "TASK-AUTO-FINAL-1", "goal": "First Final Test"})
    controller.loop.queue.add_task({"task_id": "TASK-AUTO-FINAL-2", "goal": "Second Final Test"})
    controller.loop.queue.add_task({"task_id": "TASK-AUTO-FINAL-3", "goal": "Third Final Test"})

    result = controller.run_cycle(max_tasks=3)
    print(f"Cycle Result: {result['status']} (Tasks: {len(result['tasks_processed'])})")
    
    if result['status'] == "completed" and len(result['tasks_processed']) == 3:
        print("Smoke Test PASSED ✅")
    else:
        print("Smoke Test FAILED ❌")
        exit(1)
