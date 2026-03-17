import json
import os
from datetime import datetime
from core.autonomous_loop import AutonomousLoop
from core.orchestrator import Orchestrator

class FullAutonomyController:
    def __init__(self, queue_dir: str = "tasks/queue", processed_dir: str = "tasks/processed"):
        self.loop = AutonomousLoop(queue_dir, processed_dir)
        self.queue = self.loop.queue

    def start_mission(self, duration_steps: int = 1) -> dict:
        report = {"start_time": datetime.now().isoformat(), "steps_completed": 0, "logs": []}
        
        # 1. Generate Task
        self.queue.add_task({"task_id": "AUTO-GEN-1", "goal": "Self-check"})
        report["logs"].append("Generated task AUTO-GEN-1")

        # 2. Run Loop
        for _ in range(duration_steps):
            res = self.loop.run_once()
            report["logs"].append(f"Loop result: {res['status']}")
            if res['status'] == "completed": report["steps_completed"] += 1
            
        return report

if __name__ == "__main__":
    # Mock LLM injection for test
    from core.autonomous_loop import LLMAdapter
    class MockLLM(LLMAdapter):
        def generate_response(self, prompt, **kwargs): return "step1|echo 'Autonomy'"
        def get_model_info(self): return {"name": "mock"}
        def stream_response(self, p, **kwargs): yield "ok"
        def chat_completion(self, m, **kwargs): return "ok"
        
    ctrl = FullAutonomyController(queue_dir="tasks/queue_auto", processed_dir="tasks/processed_auto")
    ctrl.loop.llm = MockLLM()
    if ctrl.loop.orchestrator is None:
        ctrl.loop.orchestrator = Orchestrator(ctrl.loop.llm)
    else:
        ctrl.loop.orchestrator.llm = ctrl.loop.llm
    
    res = ctrl.start_mission()
    if res['steps_completed'] >= 1: print("Smoke Test PASSED ✅")
    else: print("Smoke Test FAILED ❌")
