import unittest
from unittest.mock import patch

from adapters.llm.llm_adapter import LLMAdapter
from core.event_bus import EventBus
from core.event_types import EventTypes
from core.orchestrator import Orchestrator, OrchestratorStep


class DummyLLM(LLMAdapter):
    def generate_response(self, prompt: str, **kwargs) -> tuple[str, int, int]:
        return "dummy", 0, 0

    def get_model_info(self) -> dict:
        return {"name": "dummy", "provider": "test"}

    def stream_response(self, prompt: str, **kwargs):
        yield self.generate_response(prompt)[0]

    def chat_completion(self, messages: list[dict], **kwargs) -> tuple[str, int, int]:
        return self.generate_response(messages[-1]["content"] if messages else "")


class OrchestratorReplanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.events: list[dict] = []
        self.bus = EventBus()
        self.bus.subscribe(EventTypes.REPLAN_READY, lambda event: self.events.append(event))
        self.bus.subscribe(EventTypes.REPLAN_EXECUTED, lambda event: self.events.append(event))
        self.orch = Orchestrator(DummyLLM(), event_bus=self.bus)

    def test_replan_triggers_on_error(self):
        workflow_result = {
            "results": [
                {"name": "critical_step", "status": "error", "stderr": "permission denied while writing"}
            ]
        }
        replan = self.orch.replan_on_failure(workflow_result)
        self.assertEqual(replan["status"], "replan_ready")
        self.assertEqual(replan["hint"], "elevate_permissions")
        self.assertGreater(len(replan["new_plan"]), 0)
        self.assertIn("replan", replan["new_plan"][0]["name"])

    def test_no_replan_for_success(self):
        workflow_result = {"results": [{"name": "ok", "status": "success", "stderr": ""}]}
        self.assertEqual(self.orch.replan_on_failure(workflow_result)["status"], "no_replan_needed")

    @patch("core.orchestrator.run_workflow")
    def test_execute_plan_runs_replan_sequence(self, mock_run_workflow):
        initial_result = {
            "status": "stopped",
            "results": [
                {"name": "critical_step", "status": "error", "stderr": "permission denied while writing"}
            ],
        }
        replan_result = {
            "status": "completed",
            "results": [{"name": "replan_inspect", "status": "success", "stderr": ""}],
        }
        mock_run_workflow.side_effect = [initial_result, replan_result]

        steps = [OrchestratorStep(name="initial", instruction="echo fail")]
        result = self.orch.execute_plan(steps)

        self.assertIn("replan", result)
        self.assertEqual(result["replan"]["info"]["status"], "replan_ready")
        self.assertEqual(result["replan"]["execution"], replan_result)
        self.assertGreater(len(result["replan"]["steps"]), 0)
        self.assertEqual(mock_run_workflow.call_count, 2)
        self.assertEqual(len(self.events), 2)
        self.assertEqual(self.events[0]["type"], EventTypes.REPLAN_READY)
        self.assertEqual(self.events[1]["type"], EventTypes.REPLAN_EXECUTED)
        self.assertEqual(self.events[0]["payload"].get("workflow_name"), "orchestrator-plan")


if __name__ == "__main__":
    unittest.main()
