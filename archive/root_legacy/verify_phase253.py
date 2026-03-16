
import os
import json
import glob
from datetime import datetime
from core.task_queue import TaskQueue

# Define paths
GRAYWOLF_ROOT = '/home/adem/graywolf'
QUEUE_DIR = os.path.join(GRAYWOLF_ROOT, 'tasks/queue')
PROCESSED_DIR = os.path.join(GRAYWOLF_ROOT, 'tasks/processed')
EVIDENCE_PATH = os.path.join(GRAYWOLF_ROOT, 'reports/evidence/phase253/')
EVIDENCE_FILE = os.path.join(EVIDENCE_PATH, 'queue_system_evidence.json')

# Ensure evidence directory exists
os.makedirs(EVIDENCE_PATH, exist_ok=True)

queue = TaskQueue(queue_dir=QUEUE_DIR, processed_dir=PROCESSED_DIR)

# Clear previous tasks for a clean test run
for f in glob.glob(os.path.join(queue.queue_dir, '*.json')):
    os.remove(f)
for f in glob.glob(os.path.join(queue.processed_dir, '*.json')):
    os.remove(f)

# Add at least two tasks for verification
new_task_1 = {'task_id': 'TASK-001-VERIFY', 'name': 'Verify Task 1', 'description': 'First task for verification.'}
queue.add_task(new_task_1)

new_task_2 = {'task_id': 'TASK-002-VERIFY', 'name': 'Verify Task 2', 'description': 'Second task for verification.'}
queue.add_task(new_task_2)

# Capture initial queued tasks snapshot
initial_queued_tasks_snapshot = [
    f.split(os.sep)[-1].replace('.json', '')
    for f in sorted(glob.glob(os.path.join(queue.queue_dir, '*.json')))
]

# Process tasks
processed_tasks_list = []
processing_order = []

print("--- Starting task processing for Phase 253 verification ---")
while True:
    task = queue.get_next_task()
    if not task:
        print("No more tasks in queue.")
        break

    task_id = task['task_id']
    processing_order.append(task_id)
    print(f'Processing task: {task_id}')

    # Simulate task processing and generate a result
    result = {'message': f'Task {task_id} processed successfully during verification.'}
    processed_tasks_list.append(task_id)
    queue.mark_processed(task_id, status='completed', result=result)

print(f'Processed tasks: {processed_tasks_list}')
print(f'Processing order: {processing_order}')

# Get current tasks in queue for evidence (should be empty after processing)
remaining_queued_tasks = [
    f.split(os.sep)[-1].replace('.json', '')
    for f in sorted(glob.glob(os.path.join(queue.queue_dir, '*.json')))
]

# Determine final status
# VERIFIED if at least 2 tasks were processed and the queue is empty afterwards
final_status = 'PARTIAL'
if len(processed_tasks_list) >= 2 and len(remaining_queued_tasks) == 0:
    final_status = 'VERIFIED'
elif len(processed_tasks_list) > 0 and len(remaining_queued_tasks) > 0:
    final_status = 'PARTIAL' # Some tasks processed, but not all or not enough initially

evidence_data = {
    'queue_path': queue.queue_dir,
    'initial_queued_tasks_snapshot': initial_queued_tasks_snapshot,
    'processed_tasks': processed_tasks_list,
    'processing_order': processing_order,
    'remaining_queued_tasks': remaining_queued_tasks,
    'final_status': final_status
}

with open(EVIDENCE_FILE, 'w') as f:
    json.dump(evidence_data, f, indent=2)

print(f'Evidence written to {EVIDENCE_FILE}')
