
import os
import sys
import json
import glob

# Ensure GrayWolf root is in sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = script_dir # Assuming this script is at /home/adem/graywolf/
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dashboard.dashboard_generator import DashboardGenerator
from core.task_queue import TaskQueue # For setting up initial tasks

def run_monitoring_dashboard_test():
    print("--- Running Phase 259 Monitoring Dashboard Test ---")
    
    # Setup initial tasks for the dashboard to read
    queue_dir = os.path.join(project_root, "tasks", "queue")
    processed_dir = os.path.join(project_root, "tasks", "processed")
    task_queue = TaskQueue(queue_dir=queue_dir, processed_dir=processed_dir)

    # Generate dashboard snapshot
    evidence_output_dir = os.path.join(project_root, "reports", "evidence", "phase259")
    generator = DashboardGenerator(
        output_dir=evidence_output_dir,
        queue_dir=queue_dir,
        processed_dir=processed_dir
    )
    snapshot_data = generator.generate_snapshot()
    
    print(json.dumps(snapshot_data, indent=2))

    # Verify contents of the snapshot
    overall_test_status = "FAILED"
    expected_active_tasks = 1 # DASH-TASK-002
    expected_completed_tasks = 1 # DASH-TASK-001
    expected_total_tasks = 2
    expected_last_task_id = "DASH-TASK-001"

    metrics = snapshot_data.get("metrics", {})
    if (metrics.get("active_tasks") == expected_active_tasks and
        metrics.get("completed_tasks") == expected_completed_tasks and
        metrics.get("total_tasks") == expected_total_tasks and
        metrics.get("last_task_id") == expected_last_task_id and
        snapshot_data.get("status") == "online"):
        overall_test_status = "VERIFIED"
    
    if overall_test_status == "VERIFIED":
        print("Phase 259 Verification Test PASSED ✅")
    else:
        print("Phase 259 Verification Test FAILED ❌")
        sys.exit(1)

if __name__ == "__main__":
    run_monitoring_dashboard_test()
