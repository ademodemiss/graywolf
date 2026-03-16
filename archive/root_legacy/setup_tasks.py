import os
import glob
import json
import sys

# Add project root to path to allow importing core modules
sys.path.append("/home/adem/graywolf")
from core.task_queue import TaskQueue

def setup_sequential_tasks():
    """Clears the task queue and adds 3 new sequential tasks."""
    print("Setting up tasks for the autonomous run...")
    
    queue_dir = "/home/adem/graywolf/tasks/queue"
    processed_dir = "/home/adem/graywolf/tasks/processed"
    
    # 1. Initialize TaskQueue
    task_queue = TaskQueue(queue_dir=queue_dir, processed_dir=processed_dir)
    
    # 2. Clear existing tasks in queue and processed folders for a clean run
    for dir_path in [queue_dir, processed_dir]:
        files = glob.glob(os.path.join(dir_path, "*.json"))
        for f in files:
            os.remove(f)
    print(f"Cleared {len(files)} files from previous runs.")
            
    # 3. Define and add 3 sequential tasks
    tasks = [
        {"task_id": "TASK-SEQ-001", "goal": "Run initial system diagnostics and save to a file."},
        {"task_id": "TASK-SEQ-002", "goal": "Analyze diagnostics file for anomalies and log findings."},
        {"task_id": "TASK-SEQ-003", "goal": "Generate a final summary report based on the analysis log."}
    ]
    
    for task in tasks:
        task_queue.add_task(task)
        print(f"Added task: {task['task_id']}")
        
    print("Task setup complete. 3 tasks added to the queue.")

if __name__ == "__main__":
    setup_sequential_tasks()
