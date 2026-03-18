import sys
import glob
import json
import os
from datetime import datetime

class DashboardGenerator:
    def __init__(self, output_dir: str = "reports/dashboard", queue_dir: str = "tasks/queue", processed_dir: str = "tasks/processed"):
        self.output_dir = output_dir
        self.queue_dir = queue_dir
        self.processed_dir = processed_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_snapshot(self) -> dict:
        # Ensure GrayWolf root is in sys.path for internal imports
        if "/home/adem/graywolf" not in sys.path:
            sys.path.insert(0, "/home/adem/graywolf")

        try:
            from core.task_queue import TaskQueue
            # from core.autonomous_loop import AutonomousLoop # Not directly needed for snapshot metrics
        except ImportError as e:
            print(f"Error importing GrayWolf core modules in DashboardGenerator: {e}")
            # Fallback to static data if imports fail
            return {"status": "error", "timestamp": datetime.now().isoformat(), "metrics": {"tasks": -1, "success": -1, "error": str(e)}}

        # Initialize TaskQueue to get task counts using provided paths
        queue = TaskQueue(queue_dir=self.queue_dir, processed_dir=self.processed_dir)
        queue_status = queue.get_queue_status()

        # Get last processed task (simplistic for now, from processed_dir)
        last_task_id = "N/A"
        processed_files = sorted(glob.glob(os.path.join(self.processed_dir, "*.json")), key=os.path.getmtime, reverse=True)
        if processed_files:
            try:
                with open(processed_files[0], "r") as f:
                    last_task_data = json.load(f)
                    last_task_id = last_task_data.get("task_id", "N/A")
            except Exception as e:
                print(f"Error reading last processed task: {e}")

        # Mock last commit/report for now, as Git integration and full report generation are in other phases
        last_commit = "mock_commit_hash_123"
        last_report = "mock_report_xyz"

        snap = {
            "status": "online",
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "active_tasks": queue_status.get("queued_count", 0),
                "completed_tasks": queue_status.get("processed_count", 0),
                "total_tasks": queue_status.get("queued_count", 0) + queue_status.get("processed_count", 0),
                "last_task_id": last_task_id,
                "last_commit_hash": last_commit,
                "last_report_id": last_report
            }
        }
        with open(os.path.join(self.output_dir, "snapshot.json"), "w") as f: json.dump(snap, f, indent=2)
        return snap

if __name__ == "__main__":
    gen = DashboardGenerator(output_dir="reports/evidence/phase259")
    if gen.generate_snapshot()['status'] == "online": print("Smoke Test PASSED ✅")
    else: print("Smoke Test FAILED ❌")
