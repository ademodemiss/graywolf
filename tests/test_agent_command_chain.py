from pathlib import Path

from agent.command_parser import parse_command
from agent.task_decomposer import decompose_plan
from agent.dispatcher import Dispatcher


def test_parse_command_basic():
    out = parse_command("Sistemde sağlık kontrolü yap")
    assert out["objective"]
    assert out["intent"] in {"healthcheck", "execute", "analyze", "deploy"}


def test_decompose_plan_single_step():
    steps = decompose_plan("deploy hazırlığı yap")
    assert len(steps) == 1
    assert steps[0]["id"] == "step-1"
    assert "goal" in steps[0]["payload"]


def test_dispatcher_queues_task(tmp_path: Path):
    queue_dir = tmp_path / "queue"
    processed_dir = tmp_path / "processed"
    d = Dispatcher(queue_dir=str(queue_dir), processed_dir=str(processed_dir))

    result = d.dispatch("healthcheck başlat")
    assert result["steps_executed"]
    assert result["steps_executed"][0]["status"] in {"queued", "confirm_required", "denied"}
