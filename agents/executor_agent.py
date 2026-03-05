from dataclasses import dataclass

from workflows.runner import run_workflow


@dataclass
class ExecutorAgent:
    def execute(self, workflow: dict) -> dict:
        wf = {
            "name": workflow.get("name", "agent-execution"),
            "continue_on_error": True,
            "steps": workflow.get("steps", []),
        }
        return run_workflow(wf)
