from concurrent.futures import ThreadPoolExecutor
import datetime
import shlex
import subprocess


class NodeWorkerPool:
    def __init__(self, max_workers: int = 4):
        self.pool = ThreadPoolExecutor(max_workers=max_workers)

    def submit_task(self, task: str):
        return self.pool.submit(self._run_task, task)

    @staticmethod
    def _run_task(task: str) -> dict:
        started = datetime.datetime.now(datetime.timezone.utc).isoformat()
        cmd = shlex.split(task)
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120, check=False)
        return {
            "started_at": started,
            "task": task,
            "exit_code": res.returncode,
            "stdout": (res.stdout or "").strip(),
            "stderr": (res.stderr or "").strip(),
        }
