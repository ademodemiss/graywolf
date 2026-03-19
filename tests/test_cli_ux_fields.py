import json
import subprocess
from pathlib import Path


ROOT = Path("/home/adem/graywolf")
CLI = ROOT / "scripts" / "graywolf"


def _run_cli(*args: str) -> dict:
    p = subprocess.run([str(CLI), *args], capture_output=True, text=True, check=False)
    assert p.stdout.strip(), f"empty stdout for args={args}, stderr={p.stderr}"
    payload = json.loads(p.stdout.strip().splitlines()[-1])
    return payload


def _assert_ux(payload: dict):
    ux = payload.get("ux")
    assert isinstance(ux, dict), payload
    assert isinstance(ux.get("summary"), str) and ux.get("summary"), payload
    assert isinstance(ux.get("next_step"), str) and ux.get("next_step"), payload


def test_run_has_ux_fields():
    out = _run_cli("run", "--intent", "healthcheck", "--goal", "ux-contract-test")
    _assert_ux(out)


def test_approvals_has_ux_fields():
    out = _run_cli("approvals")
    _assert_ux(out)


def test_approve_has_ux_fields_even_on_error():
    out = _run_cli("approve", "APR-DOES-NOT-EXIST-TEST")
    _assert_ux(out)


def test_deny_has_ux_fields_even_on_error():
    out = _run_cli("deny", "APR-DOES-NOT-EXIST-TEST")
    _assert_ux(out)


def test_status_has_ux_fields():
    out = _run_cli("status", "--session-id", "ux-contract-suite")
    _assert_ux(out)


def test_queue_has_ux_fields():
    out = _run_cli("queue", "--limit", "3")
    _assert_ux(out)


def test_monitor_status_has_ux_fields():
    out = _run_cli("monitor", "status")
    _assert_ux(out)


def test_doctor_has_ux_fields():
    out = _run_cli("doctor")
    _assert_ux(out)


def test_report_has_ux_fields():
    out = _run_cli("report", "daily")
    _assert_ux(out)


def test_help_has_ux_fields():
    out = _run_cli("help")
    _assert_ux(out)
