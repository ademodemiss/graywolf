"""DEPRECATED: use `jobqueue` package.
Temporary compatibility shim (planned removal in 2 weeks).
Also re-exports stdlib queue symbols to avoid import breakage.
"""

from importlib import util as _import_util
from pathlib import Path as _Path

_stdlib_queue_path = _Path('/usr/lib/python3.12/queue.py')
_spec = _import_util.spec_from_file_location('_stdlib_queue', str(_stdlib_queue_path))
_stdq = _import_util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_stdq)

# stdlib-compatible exports
Queue = _stdq.Queue
LifoQueue = _stdq.LifoQueue
PriorityQueue = _stdq.PriorityQueue
SimpleQueue = getattr(_stdq, 'SimpleQueue', Queue)
Empty = _stdq.Empty
Full = _stdq.Full

# jobqueue back-compat exports
from jobqueue.task_queue import *  # noqa: F401,F403
from jobqueue.job_scheduler import *  # noqa: F401,F403
from jobqueue.job_worker import *  # noqa: F401,F403
from jobqueue.job_status import *  # noqa: F401,F403
from jobqueue.queue_storage import *  # noqa: F401,F403
