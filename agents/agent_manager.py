import argparse
import json

from agents.executor_agent import ExecutorAgent
from agents.monitor_agent import MonitorAgent
from agents.planner_agent import PlannerAgent


class AgentManager:
    def __init__(self):
        self.planner = PlannerAgent()
        self.executor = ExecutorAgent()
        self.monitor = MonitorAgent()

    def run(self, goal: str) -> dict:
        plan = self.planner.plan(goal)
        execution = self.executor.execute(plan)
        monitor = self.monitor.check(execution)
        return {
            "goal": goal,
            "planner": {"status": "plan_generated", "source": plan.get("source", "unknown"), "steps": plan.get("steps", [])},
            "executor": {"status": "steps_executed", "execution": execution},
            "monitor": {"status": "status_ok" if monitor.get("status") == "ok" else "status_warning", "detail": monitor},
        }


def main():
    parser = argparse.ArgumentParser(description="GrayWolf multi-agent manager")
    parser.add_argument("--goal", required=True)
    args = parser.parse_args()

    result = AgentManager().run(args.goal)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
