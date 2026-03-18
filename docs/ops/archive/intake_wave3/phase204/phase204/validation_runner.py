import argparse
import threading
import time
from pathlib import Path

from core.approval import ApprovalManager, ApprovalState
from core.event_types import EventTypes
from monitor.approval_notifier import ApprovalNotifier
from policies.shell_policy import ShellPolicy


LOG_PATH = Path("logs/phase204_validation.log")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


class ValidationRunner:
    def __init__(self, manager: ApprovalManager | None = None, notifier: ApprovalNotifier | None = None):
        policy = ShellPolicy()
        self.manager = manager or ApprovalManager(policy=policy)
        self.notifier = notifier or ApprovalNotifier()

    def run(self, command: str, auto: str | None = None, delay: float = 1.0, timeout: float = 30.0) -> ApprovalState | None:
        request, message = self.manager.evaluate_command(command, requested_by="validation-runner", category_hint="phase204-validation")
        self._log(f"Evaluated command '{command}' -> {message}")

        if not request or request.status == ApprovalState.GRANTED:
            self._log(f"Executing command immediately: {command}")
            return ApprovalState.GRANTED

        if request.status == ApprovalState.DENIED:
            self._log(f"Command denied by policy: {command}")
            return ApprovalState.DENIED

        if auto in {"grant", "deny"}:
            threading.Thread(target=self._auto_respond, args=(request.request_id, auto, delay), daemon=True).start()

        final = self.manager.wait_for_status(request.request_id, {ApprovalState.GRANTED, ApprovalState.DENIED}, timeout_seconds=int(timeout))
        if final is None:
            self._log(f"Approval timeout after {timeout}s for {request.request_id}")
            return None

        self._log(f"Approval {final.status} for {command} (request {request.request_id})")
        return final.status

    def _auto_respond(self, request_id: str, mode: str, delay: float) -> None:
        time.sleep(delay)
        target = EventTypes.APPROVAL_GRANTED if mode == "grant" else EventTypes.APPROVAL_DENIED
        request = self.manager.get_request(request_id)
        if request:
            self.manager.bus.publish(target, request.to_payload())
            self._log(f"Auto-{mode} published for {request_id}")

    def _log(self, message: str) -> None:
        entry = {
            "ts": time.time(),
            "message": message,
        }
        with open(LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(f"{entry}\n")


def run_from_cli() -> None:
    parser = argparse.ArgumentParser(description="Phase 204 approval validation runner")
    parser.add_argument("command", help="Shell command descriptor that might need approval")
    parser.add_argument("--auto", choices=["grant", "deny"], help="Auto respond after delay")
    parser.add_argument("--delay", type=float, default=1.0, help="Seconds before auto-response")
    parser.add_argument("--timeout", type=float, default=30.0, help="Seconds to wait for approval")
    args = parser.parse_args()

    runner = ValidationRunner()
    status = runner.run(args.command, auto=args.auto, delay=args.delay, timeout=args.timeout)
    if status == ApprovalState.GRANTED:
        print("Command approved and ready to run.")
    elif status == ApprovalState.DENIED:
        print("Command denied - will not execute.")
    else:
        print("Approval timeout or unknown status; manual intervention needed.")


if __name__ == "__main__":
    run_from_cli()
