from dataclasses import dataclass

from core.llm_router import LLMRouter


@dataclass
class PlannerAgent:
    use_llm: bool = True

    def _fallback_plan(self, goal: str) -> list[dict]:
        g = (goal or "").lower()
        if "healthcheck" in g:
            return [
                {"name": "check-python", "cmd": "python3 --version"},
                {"name": "check-pip", "cmd": "pip --version"},
                {"name": "check-policy", "cmd": "rm -rf /", "continue_on_error": True},
            ]
        return [
            {"name": "list-repo", "cmd": "ls -1 /home/adem/graywolf"},
            {"name": "status-report", "cmd": "python3 -m monitor.heartbeat --test", "continue_on_error": True},
        ]

    def plan(self, goal: str) -> dict:
        if not self.use_llm:
            return {"name": "planner-fallback", "steps": self._fallback_plan(goal), "source": "fallback"}

        prompt = (
            "Return max 3 lines in format step_name|shell_command. "
            "No explanations. Goal: " + (goal or "")
        )
        try:
            llm = LLMRouter().get()
            raw = llm.generate_response(prompt)
            steps = []
            for line in (raw or "").splitlines():
                if "|" not in line:
                    continue
                name, cmd = line.split("|", 1)
                name, cmd = name.strip(), cmd.strip()
                if name and cmd:
                    steps.append({"name": name, "cmd": cmd})
            if not steps:
                steps = self._fallback_plan(goal)
                source = "fallback"
            else:
                source = "llm"
            return {"name": "planner-workflow", "steps": steps[:3], "source": source}
        except Exception:
            return {"name": "planner-fallback", "steps": self._fallback_plan(goal), "source": "fallback"}
