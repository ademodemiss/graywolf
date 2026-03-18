import os
import json
import glob
from datetime import datetime
from typing import Dict, Optional

class TaskQueue:
    def __init__(self, queue_dir: str = "tasks/queue", processed_dir: str = "tasks/processed"):
        self.queue_dir = queue_dir
        self.processed_dir = processed_dir
        os.makedirs(self.queue_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)

    def add_task(self, task: Dict) -> str:
        task_id = task.get("task_id")
        if not task_id:
            raise ValueError("Task must have task_id")
        
        task["status"] = "queued"
        task["queued_at"] = datetime.now().isoformat()
        
        path = os.path.join(self.queue_dir, f"{task_id}.json")
        with open(path, "w") as f:
            json.dump(task, f, indent=2)
        return path

    def get_next_task(self) -> Optional[Dict]:
        files = sorted(glob.glob(os.path.join(self.queue_dir, "*.json")))
        if not files:
            return None
            
        next_file = files[0]
        with open(next_file, "r") as f:
            task = json.load(f)
        return task

    def mark_processed(self, task_id: str, status: str = "completed", result: Dict = None):
        src = os.path.join(self.queue_dir, f"{task_id}.json")
        if not os.path.exists(src):
            return
            
        with open(src, "r") as f:
            task = json.load(f)
            
        task["status"] = status
        task["processed_at"] = datetime.now().isoformat()
        if result:
            task["result"] = result
            
        dst = os.path.join(self.processed_dir, f"{task_id}.json")
        with open(dst, "w") as f:
            json.dump(task, f, indent=2)
            
        os.remove(src)
        return dst

    def get_queue_status(self) -> Dict:
        queued = len(glob.glob(os.path.join(self.queue_dir, "*.json")))
        processed = len(glob.glob(os.path.join(self.processed_dir, "*.json")))
        return {"queued_count": queued, "processed_count": processed}
