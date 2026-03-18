# Deprecation Matrix (Runtime/Workflow Conflicts)

_Last updated: 2026-03-17_

| Area | File | Current status | Decision | Action |
|---|---|---|---|---|
| Runtime | `core/autonomous_loop.py` | Active | KEEP | Canonical runtime loop |
| Runtime | `scripts/run_autonomy_worker.py` | Active | KEEP | Canonical worker entry |
| Runtime | `scripts/autonomy_daemon.sh` | Active | KEEP | Canonical daemon control |
| Runtime | `archive/runtime_legacy/full_autonomy.py` | Archived | COMPLETE | Legacy path removed from active core |
| Runtime | `archive/runtime_legacy/full_autonomy_controller.py` | Archived | COMPLETE | Legacy path removed from active core |
| Runtime | `archive/runtime_legacy/agent_loop.py` | Archived | COMPLETE | Secondary loop path archived |
| Runtime | `archive/runtime_legacy/service_runner.py` | Archived | COMPLETE | Wrapper path archived |
| Workflow | `workflows/runner.py` | Active | KEEP | Canonical workflow executor |
| Workflow | `archive/workflow_legacy/workflow_executor.py` | Archived | COMPLETE | Compatibility executor archived |
| Intake | `archive/agent_legacy/command_parser.py` | Archived | COMPLETE | Prototype archived |
| Intake | `archive/agent_legacy/task_decomposer.py` | Archived | COMPLETE | Prototype archived |
| Intake | `archive/agent_legacy/dispatcher.py` | Archived | COMPLETE | Prototype archived |
| Goal | `goals/goal_router.py` | Stub | PENDING | Keep as spec stub or archive |
| Goal | `goals/goal_interface.py` | Stub | PENDING | Keep as spec stub or archive |
| Capability | `capabilities/registry.py` | Stub | PENDING | Replace/expand or archive |

## Rules
1. Canonical olmayan dosyalara yeni özellik eklenmez.
2. Yeni geliştirme yalnız canonical hat üzerinde yapılır.
3. Deprecate dosyalar silinmeden önce çağıran yerler `rg` ile temizlenir.
