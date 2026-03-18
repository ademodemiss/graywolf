import json
import os
from datetime import datetime
from core.task_queue import TaskQueue

EVIDENCE_DIR = "reports/evidence/phase253"
os.makedirs(EVIDENCE_DIR, exist_ok=True)

def main():
    print("=== Starting Phase 253: Task Queue System ===")
    
    # Initialize Queue
    queue = TaskQueue(queue_dir="tasks/queue_test", processed_dir="tasks/processed_test")
    
    # 1. Create Example Tasks
    task1 = {
        "task_id": "TASK-253-1",
        "title": "Example Task 1",
        "payload": "data_1"
    }
    task2 = {
        "task_id": "TASK-253-2",
        "title": "Example Task 2",
        "payload": "data_2"
    }
    
    print("Adding tasks to queue...")
    queue.add_task(task1)
    queue.add_task(task2)
    
    status = queue.get_queue_status()
    print(f"Queue Status: {status}")
    
    if status["queued_count"] != 2:
        raise RuntimeError("Tasks were not queued correctly")
        
    # 2. Process Tasks
    print("Processing tasks...")
    processed_count = 0
    while True:
        task = queue.get_next_task()
        if not task:
            break
            
        print(f"Processing: {task['task_id']}")
        # Simulate work
        result = {"status": "ok", "output": f"processed_{task['payload']}"}
        queue.mark_processed(task['task_id'], result=result)
        processed_count += 1
        
    print(f"Processed {processed_count} tasks.")
    
    if processed_count != 2:
        raise RuntimeError("Not all tasks were processed")
        
    final_status = queue.get_queue_status()
    print(f"Final Queue Status: {final_status}")
    
    # 3. Generate Evidence
    evidence_data = {
        "phase": 253,
        "status": "completed",
        "timestamp": datetime.now().isoformat(),
        "tasks_processed": processed_count,
        "queue_status": final_status
    }
    
    evidence_path = os.path.join(EVIDENCE_DIR, "queue_system_evidence.json")
    with open(evidence_path, "w") as f:
        json.dump(evidence_data, f, indent=2)
        
    print(f"Evidence saved to: {evidence_path}")
    print("=== Phase 253 COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        exit(1)
