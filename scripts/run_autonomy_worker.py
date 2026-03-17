#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, "/home/adem/graywolf")

from core.autonomous_loop import AutonomousLoop
from core.llm_router import LLMRouter


def main() -> int:
    queue_dir = os.environ.get("GRAYWOLF_QUEUE_DIR", "/home/adem/graywolf/tasks/queue")
    processed_dir = os.environ.get("GRAYWOLF_PROCESSED_DIR", "/home/adem/graywolf/tasks/processed")

    try:
        llm = LLMRouter().get()
        loop = AutonomousLoop(queue_dir=queue_dir, processed_dir=processed_dir, llm=llm)
        result = loop.run_once()
        print(json.dumps({"ts": datetime.now().isoformat(), "result": result}, ensure_ascii=False))
        return 0
    except Exception as e:
        print(json.dumps({"ts": datetime.now().isoformat(), "status": "degraded", "error": str(e)}, ensure_ascii=False))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
