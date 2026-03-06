import argparse
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from policies.shell_policy import ShellPolicy
from tools.terminal_tool import TerminalTool
from core.idle_seed import seed_next_batch_if_idle

ROADMAP = Path('/home/adem/graywolf/docs/roadmap.md')
STATE = Path('/home/adem/graywolf/memory/agent_loop_state.json')
LOG_PATH = Path('/home/adem/graywolf/logs/terminal.log')


def normalize_milestone(s: str) -> str:
    if not s:
        return ''
    t = s.strip().lower()
    t = t.replace('—', '-').replace('–', '-')
    t = re.sub(r'\s+', ' ', t)
    return t


class AgentLoop:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.tool = TerminalTool(policy_engine=ShellPolicy(), log_dir='/home/adem/graywolf/logs')

    def _load_state(self) -> dict:
        if not STATE.exists():
            return {'completed': [], 'last_selected': None, 'last_selected_norm': None, 'last_run_ts': None, 'last_result': None}
        try:
            data = json.loads(STATE.read_text(encoding='utf-8'))
            data.setdefault('completed', [])
            data.setdefault('last_selected', None)
            data.setdefault('last_selected_norm', None)
            data.setdefault('last_run_ts', None)
            data.setdefault('last_result', None)
            return data
        except Exception:
            return {'completed': [], 'last_selected': None, 'last_selected_norm': None, 'last_run_ts': None, 'last_result': None}

    def _save_state(self, state: dict):
        STATE.parent.mkdir(parents=True, exist_ok=True)
        STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')

    def _requirements(self, milestone: str) -> dict:
        m = re.search(r'Phase\s+(\d+)', milestone)
        phase_no = int(m.group(1)) if m else 0

        plans = {

            221: {
                'files': ['/home/adem/graywolf/post_release/ops_summary.py'],
                'tests': ['python3 -m post_release.ops_summary --test'],
            },
            222: {
                'files': ['/home/adem/graywolf/post_release/service_snapshot.py'],
                'tests': ['python3 -m post_release.service_snapshot --test'],
            },
            223: {
                'files': ['/home/adem/graywolf/post_release/journal_anomaly.py'],
                'tests': ['python3 -m post_release.journal_anomaly --test'],
            },
            224: {
                'files': ['/home/adem/graywolf/post_release/heartbeat_snapshot.py'],
                'tests': ['python3 -m post_release.heartbeat_snapshot --test'],
            },
            225: {
                'files': ['/home/adem/graywolf/post_release/artifact_retention.py'],
                'tests': ['python3 -m post_release.artifact_retention --test'],
            },
            226: {
                'files': [
                    '/home/adem/graywolf/core/task_generator.py',
                    '/home/adem/graywolf/core/idle_seed.py',
                    '/home/adem/graywolf/core/service_runner.py',
                    '/home/adem/graywolf/core/task_runner.py',
                    '/home/adem/graywolf/tasks/examples/fix_semantic_search.json',
                ],
                'tests': [
                    'python3 -m py_compile /home/adem/graywolf/core/task_generator.py /home/adem/graywolf/core/idle_seed.py /home/adem/graywolf/core/service_runner.py',
                    'python3 -m core.task_generator --test',
                    'python3 -m core.idle_seed --once --cooldown 0',
                    'python3 -m core.service_runner --help',
                    'python3 -m core.task_runner --test --task /home/adem/graywolf/tasks/examples/fix_semantic_search.json',
                ],
            },
            227: {
                'files': ['/home/adem/graywolf/core/task_runner_v2.py'],
                'tests': ['python3 -m core.task_runner_v2 --test --task /home/adem/graywolf/tasks/examples/fix_semantic_search.json'],
            },
            228: {
                'files': ['/home/adem/graywolf/core/git_task_commit.py'],
                'tests': ['python3 -m core.git_task_commit --test'],
            },
            229: {
                'files': ['/home/adem/graywolf/reports/real_task_cert_v2.py'],
                'tests': ['python3 -m reports.real_task_cert_v2 --test'],
            },
            230: {
                'files': ['/home/adem/graywolf/core/git_task_commit.py'],
                'tests': [
                    'python3 -m py_compile /home/adem/graywolf/core/git_task_commit.py',
                    'python3 -m core.git_task_commit --test',
                    'python3 -m core.task_runner_v2 --test --task /home/adem/graywolf/tasks/examples/fix_semantic_search.json',
                    'python3 -m reports.real_task_cert_v2 --test',
                    'python3 -m core.git_task_commit --task /home/adem/graywolf/tasks/examples/fix_semantic_search.json --dry-run',
                    'python3 -m core.git_task_commit --task /home/adem/graywolf/tasks/examples/fix_semantic_search.json',
                ],
            },
            231: {
                'files': ['/home/adem/graywolf/core/task_replay.py'],
                'tests': ['python3 -m core.task_replay --test --task /home/adem/graywolf/tasks/examples/fix_semantic_search.json'],
            },
            232: {
                'files': ['/home/adem/graywolf/core/task_queue_runner.py'],
                'tests': ['python3 -m core.task_queue_runner --test'],
            },
            233: {
                'files': [
                    '/home/adem/graywolf/core/git_task_commit.py',
                    '/home/adem/graywolf/core/task_scope.py',
                    '/home/adem/graywolf/tasks/examples/fix_semantic_search_scope_violation.json',
                    '/home/adem/graywolf/reports/task_diff_aware_commit_report.json',
                ],
                'tests': [
                    'python3 -m py_compile /home/adem/graywolf/core/git_task_commit.py /home/adem/graywolf/core/task_scope.py',
                    'python3 -m core.git_task_commit --test',
                    'python3 -m core.git_task_commit --task /home/adem/graywolf/tasks/examples/fix_semantic_search_scope_violation.json',
                ],
            },
            234: {
                'files': [
                    '/home/adem/graywolf/tests/test_verify_fail_guardrails.py',
                    '/home/adem/graywolf/reports/verify_fail_guardrail.py',
                    '/home/adem/graywolf/tests/fixtures/tasks/verify_fail_task.json',
                    '/home/adem/graywolf/tests/fixtures/tasks/no_changes_task.json',
                    '/home/adem/graywolf/tests/fixtures/tasks/replay_mismatch_task.json',
                    '/home/adem/graywolf/reports/verify_fail_guardrail_report.json',
                ],
                'tests': [
                    'python3 -m py_compile /home/adem/graywolf/tests/test_verify_fail_guardrails.py /home/adem/graywolf/reports/verify_fail_guardrail.py',
                    'python3 -m tests.test_verify_fail_guardrails',
                    'python3 -m reports.verify_fail_guardrail',
                ],
            },
            235: {
                'files': [
                    '/home/adem/graywolf/core/evidence_integrity.py',
                    '/home/adem/graywolf/reports/evidence_integrity_chain_report.json',
                    '/home/adem/graywolf/reports/evidence_chain.json',
                ],
                'tests': [
                    'python3 -m py_compile /home/adem/graywolf/core/evidence_integrity.py',
                    'python3 -m core.evidence_integrity --test',
                    'python3 -m core.evidence_integrity --verify',
                ],
            },
            236: {
                'files': [
                    '/home/adem/graywolf/core/task_worktree.py',
                    '/home/adem/graywolf/reports/task_worktree_execution_report.json',
                ],
                'tests': [
                    'python3 -m py_compile /home/adem/graywolf/core/task_worktree.py',
                    'python3 -m core.task_worktree --test',
                ],
            },
            237: {
                'files': [
                    '/home/adem/graywolf/core/task_lock.py',
                    '/home/adem/graywolf/reports/task_locking_report.json',
                ],
                'tests': [
                    'python3 -m py_compile /home/adem/graywolf/core/task_lock.py',
                    'python3 -m core.task_lock --test',
                ],
            },
            238: {
                'files': [
                    '/home/adem/graywolf/core/task_recovery.py',
                    '/home/adem/graywolf/reports/task_recovery_report.json',
                ],
                'tests': [
                    'python3 -m py_compile /home/adem/graywolf/core/task_recovery.py',
                    'python3 -m core.task_recovery --test',
                ],
            },
            239: {
                'files': [
                    '/home/adem/graywolf/core/patch_provenance.py',
                    '/home/adem/graywolf/reports/patch_provenance_report.json',
                ],
                'tests': [
                    'python3 -m py_compile /home/adem/graywolf/core/patch_provenance.py',
                    'python3 -m core.patch_provenance --test',
                ],
            },
            240: {
                'files': [
                    '/home/adem/graywolf/core/branch_lifecycle.py',
                    '/home/adem/graywolf/reports/branch_lifecycle_report.json',
                ],
                'tests': [
                    'python3 -m py_compile /home/adem/graywolf/core/branch_lifecycle.py',
                    'python3 -m core.branch_lifecycle --test',
                ],
            },
            241: {
                'files': [
                    '/home/adem/graywolf/core/task_budget.py',
                    '/home/adem/graywolf/reports/task_budget_report.json',
                ],
                'tests': [
                    'python3 -m py_compile /home/adem/graywolf/core/task_budget.py',
                    'python3 -m core.task_budget --test',
                ],
            },
            242: {
                'files': [
                    '/home/adem/graywolf/core/task_risk.py',
                    '/home/adem/graywolf/reports/task_risk_gate_report.json',
                ],
                'tests': [
                    'python3 -m py_compile /home/adem/graywolf/core/task_risk.py',
                    'python3 -m core.task_risk --test',
                ],
            },
            243: {
                'files': [
                    '/home/adem/graywolf/core/artifact_index.py',
                    '/home/adem/graywolf/reports/artifact_index.json',
                ],
                'tests': [
                    'python3 -m py_compile /home/adem/graywolf/core/artifact_index.py',
                    'python3 -m core.artifact_index --test',
                    'python3 -m core.artifact_index --test --query TASK-001',
                ],
            },
            244: {
                'files': [
                    '/home/adem/graywolf/core/change_impact.py',
                    '/home/adem/graywolf/reports/change_impact_report.json',
                ],
                'tests': [
                    'python3 -m py_compile /home/adem/graywolf/core/change_impact.py',
                    'python3 -m core.change_impact --test',
                ],
            },
            8: {
                'files': [
                    '/home/adem/graywolf/workflow_engine/branch_executor.py',
                    '/home/adem/graywolf/workflow_engine/parallel_executor.py',
                    '/home/adem/graywolf/workflow_engine/compensation_handler.py',
                ],
                'tests': [
                    'python3 -m workflow_engine.branch_executor --test',
                    'python3 -m workflow_engine.parallel_executor --test',
                    'python3 -m workflow_engine.compensation_handler --test',
                ],
            },
            9: {
                'files': ['/home/adem/graywolf/cluster/node_manager.py', '/home/adem/graywolf/cluster/cluster_status.py'],
                'tests': ['python3 -m cluster.cluster_status'],
            },
            10: {
                'files': ['/home/adem/graywolf/agents/agent_manager.py'],
                'tests': ['python3 -m agents.agent_manager --goal "healthcheck system"'],
            },
            11: {
                'files': ['/home/adem/graywolf/memory/memory_store.py', '/home/adem/graywolf/memory/memory_search.py', '/home/adem/graywolf/memory/memory_index.py'],
                'tests': ['python3 -m memory.memory_store', 'python3 -m memory.memory_index'],
            },
            12: {
                'files': ['/home/adem/graywolf/plugins/plugin_loader.py'],
                'tests': ['python3 -m plugins.plugin_loader'],
            },
            13: {
                'files': ['/home/adem/graywolf/self_improve/code_analyzer.py', '/home/adem/graywolf/self_improve/improvement_engine.py', '/home/adem/graywolf/self_improve/patch_generator.py', '/home/adem/graywolf/self_improve/review_loop.py'],
                'tests': ['python3 -m self_improve.code_analyzer'],
            },
            14: {
                'files': ['/home/adem/graywolf/monitor/metrics_collector.py', '/home/adem/graywolf/monitor/system_monitor.py', '/home/adem/graywolf/monitor/performance_report.py'],
                'tests': ['python3 -m monitor.system_monitor', 'python3 -m monitor.performance_report'],
            },
            15: {
                'files': ['/home/adem/graywolf/infrastructure/infra_monitor.py', '/home/adem/graywolf/infrastructure/auto_scaler.py'],
                'tests': ['python3 -m infrastructure.infra_monitor', 'python3 -m infrastructure.auto_scaler --test'],
            },
            16: {
                'files': ['/home/adem/graywolf/policies/shell_policy.py', '/home/adem/graywolf/tools/terminal_tool.py'],
                'tests': ['python3 -m tools.terminal_tool --cmd "python3 -m py_compile /home/adem/graywolf/policies/shell_policy.py /home/adem/graywolf/tools/terminal_tool.py"'],
            },
            17: {
                'files': ['/home/adem/graywolf/core/event_bus.py', '/home/adem/graywolf/core/event_types.py'],
                'tests': ['python3 -m core.event_bus --test'],
            },
            18: {
                'files': ['/home/adem/graywolf/dashboard/server.py', '/home/adem/graywolf/dashboard/views.py', '/home/adem/graywolf/dashboard/data.py'],
                'tests': ['python3 -m dashboard.server --test'],
            },
            19: {
                'files': ['/home/adem/graywolf/policies/shell_policy.py', '/home/adem/graywolf/core/agent_loop.py'],
                'tests': ['python3 -m tools.terminal_tool --cmd "python3 -m py_compile /home/adem/graywolf/policies/shell_policy.py /home/adem/graywolf/core/agent_loop.py"'],
            },
            20: {
                'files': ['/home/adem/graywolf/core/agent_loop.py', '/home/adem/graywolf/core/phase_smoke.py'],
                'tests': ['python3 -m core.phase_smoke --phase 20 --test', 'python3 -m core.agent_loop --dry-run'],
            },
            21: {
                'files': ['/home/adem/graywolf/post_release/ops_smoke.py'],
                'tests': ['python3 -m post_release.ops_smoke --test'],
            },
            22: {
                'files': [
                    '/home/adem/graywolf/post_release/ops_config.py',
                    '/home/adem/graywolf/post_release/ops_monitor.py',
                    '/home/adem/graywolf/post_release/alerts.py',
                    '/home/adem/graywolf/post_release/ops_smoke.py',
                ],
                'tests': [
                    'python3 -m post_release.ops_smoke --test',
                ],
            },

            51: {
                'files': ['/home/adem/graywolf/post_release/backup_engine.py'],
                'tests': ['python3 -m post_release.backup_engine --test'],
            },
            52: {
                'files': ['/home/adem/graywolf/post_release/restore_drill.py'],
                'tests': ['python3 -m post_release.restore_drill --test'],
            },
            53: {
                'files': ['/home/adem/graywolf/post_release/disk_pressure.py'],
                'tests': ['python3 -m post_release.disk_pressure --test'],
            },
            54: {
                'files': ['/home/adem/graywolf/post_release/memory_pressure.py'],
                'tests': ['python3 -m post_release.memory_pressure --test'],
            },
            55: {
                'files': ['/home/adem/graywolf/post_release/log_integrity.py'],
                'tests': ['python3 -m post_release.log_integrity --test'],
            },
            56: {
                'files': ['/home/adem/graywolf/post_release/service_lifecycle.py'],
                'tests': ['python3 -m post_release.service_lifecycle --test'],
            },
            57: {
                'files': ['/home/adem/graywolf/post_release/journal_errors.py'],
                'tests': ['python3 -m post_release.journal_errors --test'],
            },
            58: {
                'files': ['/home/adem/graywolf/post_release/metrics_aggregator.py'],
                'tests': ['python3 -m post_release.metrics_aggregator --test'],
            },
            59: {
                'files': ['/home/adem/graywolf/post_release/alert_policy.py'],
                'tests': ['python3 -m post_release.alert_policy --test'],
            },
            60: {
                'files': ['/home/adem/graywolf/post_release/ops_runbook_generator.py'],
                'tests': ['python3 -m post_release.ops_runbook_generator --test'],
            },
            61: {
                'files': ['/home/adem/graywolf/post_release/chaos_drill.py'],
                'tests': ['python3 -m post_release.chaos_drill --test'],
            },
            62: {
                'files': ['/home/adem/graywolf/post_release/recovery_validator.py'],
                'tests': ['python3 -m post_release.recovery_validator --test'],
            },
            63: {
                'files': ['/home/adem/graywolf/post_release/incident_report.py'],
                'tests': ['python3 -m post_release.incident_report --test'],
            },
            64: {
                'files': ['/home/adem/graywolf/post_release/dashboard_feed.py'],
                'tests': ['python3 -m post_release.dashboard_feed --test'],
            },
            65: {
                'files': ['/home/adem/graywolf/post_release/config_drift.py'],
                'tests': ['python3 -m post_release.config_drift --test'],
            },
            66: {
                'files': ['/home/adem/graywolf/post_release/dependency_scan.py'],
                'tests': ['python3 -m post_release.dependency_scan --test'],
            },
            67: {
                'files': ['/home/adem/graywolf/post_release/artifact_signer.py'],
                'tests': ['python3 -m post_release.artifact_signer --test'],
            },
            68: {
                'files': ['/home/adem/graywolf/post_release/release_notes.py'],
                'tests': ['python3 -m post_release.release_notes --test'],
            },
            69: {
                'files': ['/home/adem/graywolf/post_release/stress_runner.py'],
                'tests': ['python3 -m post_release.stress_runner --test'],
            },
            70: {
                'files': ['/home/adem/graywolf/post_release/ops_certification.py'],
                'tests': ['python3 -m post_release.ops_certification --test'],
            },

            71: {
                'files': ['/home/adem/graywolf/cluster/node_registry.py'],
                'tests': ['python3 -m cluster.node_registry --test'],
            },
            72: {
                'files': ['/home/adem/graywolf/cluster/distributed_scheduler.py'],
                'tests': ['python3 -m cluster.distributed_scheduler --test'],
            },
            73: {
                'files': ['/home/adem/graywolf/agents/remote_worker.py'],
                'tests': ['python3 -m agents.remote_worker --test'],
            },
            74: {
                'files': ['/home/adem/graywolf/cluster/secure_registration.py'],
                'tests': ['python3 -m cluster.secure_registration --test'],
            },
            75: {
                'files': ['/home/adem/graywolf/cluster/health_aggregator.py'],
                'tests': ['python3 -m cluster.health_aggregator --test'],
            },
            76: {
                'files': ['/home/adem/graywolf/cluster/log_collector.py'],
                'tests': ['python3 -m cluster.log_collector --test'],
            },
            77: {
                'files': ['/home/adem/graywolf/cluster/incident_correlator.py'],
                'tests': ['python3 -m cluster.incident_correlator --test'],
            },
            78: {
                'files': ['/home/adem/graywolf/cluster/fleet_upgrade.py'],
                'tests': ['python3 -m cluster.fleet_upgrade --test'],
            },
            79: {
                'files': ['/home/adem/graywolf/dashboard/global_api.py'],
                'tests': ['python3 -m dashboard.global_api --test'],
            },
            80: {
                'files': ['/home/adem/graywolf/infrastructure/autonomous_controller.py'],
                'tests': ['python3 -m infrastructure.autonomous_controller --test'],
            },
            81: {
                'files': ['/home/adem/graywolf/ai/incident_analyzer.py'],
                'tests': ['python3 -m ai.incident_analyzer --test'],
            },
            82: {
                'files': ['/home/adem/graywolf/ai/failure_predictor.py'],
                'tests': ['python3 -m ai.failure_predictor --test'],
            },
            83: {
                'files': ['/home/adem/graywolf/ai/remediation_engine.py'],
                'tests': ['python3 -m ai.remediation_engine --test'],
            },
            84: {
                'files': ['/home/adem/graywolf/ai/alert_prioritizer.py'],
                'tests': ['python3 -m ai.alert_prioritizer --test'],
            },
            85: {
                'files': ['/home/adem/graywolf/ai/knowledge_builder.py'],
                'tests': ['python3 -m ai.knowledge_builder --test'],
            },
            86: {
                'files': ['/home/adem/graywolf/ai/self_healing.py'],
                'tests': ['python3 -m ai.self_healing --test'],
            },
            87: {
                'files': ['/home/adem/graywolf/ai/policy_optimizer.py'],
                'tests': ['python3 -m ai.policy_optimizer --test'],
            },
            88: {
                'files': ['/home/adem/graywolf/ai/ops_simulator.py'],
                'tests': ['python3 -m ai.ops_simulator --test'],
            },
            89: {
                'files': ['/home/adem/graywolf/ai/risk_assessor.py'],
                'tests': ['python3 -m ai.risk_assessor --test'],
            },
            90: {
                'files': ['/home/adem/graywolf/ai/change_manager.py'],
                'tests': ['python3 -m ai.change_manager --test'],
            },
            91: {
                'files': ['/home/adem/graywolf/ai/code_analyzer.py'],
                'tests': ['python3 -m ai.code_analyzer --test'],
            },
            92: {
                'files': ['/home/adem/graywolf/ai/patch_generator.py'],
                'tests': ['python3 -m ai.patch_generator --test'],
            },
            93: {
                'files': ['/home/adem/graywolf/ai/patch_validator.py'],
                'tests': ['python3 -m ai.patch_validator --test'],
            },
            94: {
                'files': ['/home/adem/graywolf/ai/self_improvement_loop.py'],
                'tests': ['python3 -m ai.self_improvement_loop --test'],
            },
            95: {
                'files': ['/home/adem/graywolf/deployment/autonomous_deployer.py'],
                'tests': ['python3 -m deployment.autonomous_deployer --test'],
            },
            96: {
                'files': ['/home/adem/graywolf/infrastructure/optimizer.py'],
                'tests': ['python3 -m infrastructure.optimizer --test'],
            },
            97: {
                'files': ['/home/adem/graywolf/ai/ops_intelligence.py'],
                'tests': ['python3 -m ai.ops_intelligence --test'],
            },
            98: {
                'files': ['/home/adem/graywolf/governance/autonomous_policy.py'],
                'tests': ['python3 -m governance.autonomous_policy --test'],
            },
            99: {
                'files': ['/home/adem/graywolf/governance/audit.py'],
                'tests': ['python3 -m governance.audit --test'],
            },
            100: {
                'files': ['/home/adem/graywolf/governance/platform_certification.py'],
                'tests': ['python3 -m governance.platform_certification --test'],
            },

            101: {
                'files': ['/home/adem/graywolf/ai/task_planner.py'],
                'tests': ['python3 -m ai.task_planner --test'],
            },
            102: {
                'files': ['/home/adem/graywolf/ai/goal_manager.py'],
                'tests': ['python3 -m ai.goal_manager --test'],
            },
            103: {
                'files': ['/home/adem/graywolf/ai/memory_retrieval.py'],
                'tests': ['python3 -m ai.memory_retrieval --test'],
            },
            104: {
                'files': ['/home/adem/graywolf/ai/context_builder.py'],
                'tests': ['python3 -m ai.context_builder --test'],
            },
            105: {
                'files': ['/home/adem/graywolf/ai/decision_engine.py'],
                'tests': ['python3 -m ai.decision_engine --test'],
            },
            106: {
                'files': ['/home/adem/graywolf/ai/task_queue.py'],
                'tests': ['python3 -m ai.task_queue --test'],
            },
            107: {
                'files': ['/home/adem/graywolf/ai/reasoning_trace.py'],
                'tests': ['python3 -m ai.reasoning_trace --test'],
            },
            108: {
                'files': ['/home/adem/graywolf/ai/action_validator.py'],
                'tests': ['python3 -m ai.action_validator --test'],
            },
            109: {
                'files': ['/home/adem/graywolf/ai/policy_guard.py'],
                'tests': ['python3 -m ai.policy_guard --test'],
            },
            110: {
                'files': ['/home/adem/graywolf/ai/planning_loop.py'],
                'tests': ['python3 -m ai.planning_loop --test'],
            },
            111: {
                'files': ['/home/adem/graywolf/ai/codebase_analyzer.py'],
                'tests': ['python3 -m ai.codebase_analyzer --test'],
            },
            112: {
                'files': ['/home/adem/graywolf/ai/bug_detector.py'],
                'tests': ['python3 -m ai.bug_detector --test'],
            },
            113: {
                'files': ['/home/adem/graywolf/ai/patch_generator_v2.py'],
                'tests': ['python3 -m ai.patch_generator_v2 --test'],
            },
            114: {
                'files': ['/home/adem/graywolf/ai/patch_sandbox.py'],
                'tests': ['python3 -m ai.patch_sandbox --test'],
            },
            115: {
                'files': ['/home/adem/graywolf/ai/patch_approval.py'],
                'tests': ['python3 -m ai.patch_approval --test'],
            },
            116: {
                'files': ['/home/adem/graywolf/ai/self_improve_scheduler.py'],
                'tests': ['python3 -m ai.self_improve_scheduler --test'],
            },
            117: {
                'files': ['/home/adem/graywolf/ai/learning_store.py'],
                'tests': ['python3 -m ai.learning_store --test'],
            },
            118: {
                'files': ['/home/adem/graywolf/ai/strategy_eval.py'],
                'tests': ['python3 -m ai.strategy_eval --test'],
            },
            119: {
                'files': ['/home/adem/graywolf/ai/improvement_sim.py'],
                'tests': ['python3 -m ai.improvement_sim --test'],
            },
            120: {
                'files': ['/home/adem/graywolf/ai/self_improve_loop_v2.py'],
                'tests': ['python3 -m ai.self_improve_loop_v2 --test'],
            },

            121: {
                'files': ['/home/adem/graywolf/infrastructure/infra_experiment.py'],
                'tests': ['python3 -m infrastructure.infra_experiment --test'],
            },
            122: {
                'files': ['/home/adem/graywolf/infrastructure/benchmark_runner.py'],
                'tests': ['python3 -m infrastructure.benchmark_runner --test'],
            },
            123: {
                'files': ['/home/adem/graywolf/infrastructure/resource_optimizer_ai.py'],
                'tests': ['python3 -m infrastructure.resource_optimizer_ai --test'],
            },
            124: {
                'files': ['/home/adem/graywolf/ai/load_predictor.py'],
                'tests': ['python3 -m ai.load_predictor --test'],
            },
            125: {
                'files': ['/home/adem/graywolf/ai/failure_model.py'],
                'tests': ['python3 -m ai.failure_model --test'],
            },
            126: {
                'files': ['/home/adem/graywolf/infrastructure/adaptive_scaler.py'],
                'tests': ['python3 -m infrastructure.adaptive_scaler --test'],
            },
            127: {
                'files': ['/home/adem/graywolf/infrastructure/experiment_analyzer.py'],
                'tests': ['python3 -m infrastructure.experiment_analyzer --test'],
            },
            128: {
                'files': ['/home/adem/graywolf/infrastructure/optimization_policy.py'],
                'tests': ['python3 -m infrastructure.optimization_policy --test'],
            },
            129: {
                'files': ['/home/adem/graywolf/infrastructure/change_risk_predictor.py'],
                'tests': ['python3 -m infrastructure.change_risk_predictor --test'],
            },
            130: {
                'files': ['/home/adem/graywolf/infrastructure/infra_tuning.py'],
                'tests': ['python3 -m infrastructure.infra_tuning --test'],
            },

            131: {
                'files': ['/home/adem/graywolf/infrastructure/reserved_131.py'],
                'tests': ['python3 -m infrastructure.reserved_131 --test'],
            },
            132: {
                'files': ['/home/adem/graywolf/infrastructure/reserved_132.py'],
                'tests': ['python3 -m infrastructure.reserved_132 --test'],
            },
            133: {
                'files': ['/home/adem/graywolf/infrastructure/reserved_133.py'],
                'tests': ['python3 -m infrastructure.reserved_133 --test'],
            },
            134: {
                'files': ['/home/adem/graywolf/infrastructure/reserved_134.py'],
                'tests': ['python3 -m infrastructure.reserved_134 --test'],
            },
            135: {
                'files': ['/home/adem/graywolf/infrastructure/reserved_135.py'],
                'tests': ['python3 -m infrastructure.reserved_135 --test'],
            },
            136: {
                'files': ['/home/adem/graywolf/agents/communication_bus.py'],
                'tests': ['python3 -m agents.communication_bus --test'],
            },
            137: {
                'files': ['/home/adem/graywolf/agents/role_system.py'],
                'tests': ['python3 -m agents.role_system --test'],
            },
            138: {
                'files': ['/home/adem/graywolf/agents/planner_agent_v2.py'],
                'tests': ['python3 -m agents.planner_agent_v2 --test'],
            },
            139: {
                'files': ['/home/adem/graywolf/agents/executor_agent_v2.py'],
                'tests': ['python3 -m agents.executor_agent_v2 --test'],
            },
            140: {
                'files': ['/home/adem/graywolf/agents/auditor_agent_v2.py'],
                'tests': ['python3 -m agents.auditor_agent_v2 --test'],
            },

            141: {
                'files': ['/home/adem/graywolf/agents/consensus_engine.py'],
                'tests': ['python3 -m agents.consensus_engine --test'],
            },
            142: {
                'files': ['/home/adem/graywolf/agents/distributed_memory.py'],
                'tests': ['python3 -m agents.distributed_memory --test'],
            },
            143: {
                'files': ['/home/adem/graywolf/agents/negotiation_protocol.py'],
                'tests': ['python3 -m agents.negotiation_protocol --test'],
            },
            144: {
                'files': ['/home/adem/graywolf/agents/hierarchical_control.py'],
                'tests': ['python3 -m agents.hierarchical_control --test'],
            },
            145: {
                'files': ['/home/adem/graywolf/agents/autonomous_fleet.py'],
                'tests': ['python3 -m agents.autonomous_fleet --test'],
            },
            146: {
                'files': ['/home/adem/graywolf/ai/self_monitoring.py'],
                'tests': ['python3 -m ai.self_monitoring --test'],
            },
            147: {
                'files': ['/home/adem/graywolf/ai/risk_aware_autonomy.py'],
                'tests': ['python3 -m ai.risk_aware_autonomy --test'],
            },
            148: {
                'files': ['/home/adem/graywolf/ai/autonomous_experimentation.py'],
                'tests': ['python3 -m ai.autonomous_experimentation --test'],
            },
            149: {
                'files': ['/home/adem/graywolf/ai/self_governance.py'],
                'tests': ['python3 -m ai.self_governance --test'],
            },
            150: {
                'files': ['/home/adem/graywolf/ai/autonomous_ai_cert.py'],
                'tests': ['python3 -m ai.autonomous_ai_cert --test'],
            },

            151: {'files': ['/home/adem/graywolf/tasks/task_schema.py'], 'tests': ['python3 -m tasks.task_schema --test']},
            152: {'files': ['/home/adem/graywolf/planning/planned_actions_schema.py'], 'tests': ['python3 -m planning.planned_actions_schema --test']},
            153: {'files': ['/home/adem/graywolf/execution/safe_executor.py'], 'tests': ['python3 -m execution.safe_executor --test']},
            154: {'files': ['/home/adem/graywolf/verification/result_verifier.py'], 'tests': ['python3 -m verification.result_verifier --test']},
            155: {'files': ['/home/adem/graywolf/patching/patch_manager.py'], 'tests': ['python3 -m patching.patch_manager --test']},
            156: {'files': ['/home/adem/graywolf/analysis/failure_classifier.py'], 'tests': ['python3 -m analysis.failure_classifier --test']},
            157: {'files': ['/home/adem/graywolf/autofix/fix_loop.py'], 'tests': ['python3 -m autofix.fix_loop --test']},
            158: {'files': ['/home/adem/graywolf/reports/evidence_pack.py'], 'tests': ['python3 -m reports.evidence_pack --test']},
            159: {'files': ['/home/adem/graywolf/reports/runbook_update.py'], 'tests': ['python3 -m reports.runbook_update --test']},
            160: {'files': ['/home/adem/graywolf/reports/real_task_cert.py'], 'tests': ['python3 -m reports.real_task_cert --test']},
            161: {'files': ['/home/adem/graywolf/learning/memory_schema_v2.py'], 'tests': ['python3 -m learning.memory_schema_v2 --test']},
            162: {'files': ['/home/adem/graywolf/learning/retrieval_scoring.py'], 'tests': ['python3 -m learning.retrieval_scoring --test']},
            163: {'files': ['/home/adem/graywolf/learning/rule_extraction.py'], 'tests': ['python3 -m learning.rule_extraction --test']},
            164: {'files': ['/home/adem/graywolf/learning/regression_memory_gate.py'], 'tests': ['python3 -m learning.regression_memory_gate --test']},
            165: {'files': ['/home/adem/graywolf/learning/patch_outcome_store.py'], 'tests': ['python3 -m learning.patch_outcome_store --test']},
            166: {'files': ['/home/adem/graywolf/learning/policy_feedback.py'], 'tests': ['python3 -m learning.policy_feedback --test']},
            167: {'files': ['/home/adem/graywolf/knowledge/index_builder.py'], 'tests': ['python3 -m knowledge.index_builder --test']},
            168: {'files': ['/home/adem/graywolf/timeline/summarizer.py'], 'tests': ['python3 -m timeline.summarizer --test']},
            169: {'files': ['/home/adem/graywolf/learning/memory_consistency.py'], 'tests': ['python3 -m learning.memory_consistency --test']},
            170: {'files': ['/home/adem/graywolf/learning/learning_cert.py'], 'tests': ['python3 -m learning.learning_cert --test']},
            171: {'files': ['/home/adem/graywolf/multi_agent/role_contracts.py'], 'tests': ['python3 -m multi_agent.role_contracts --test']},
            172: {'files': ['/home/adem/graywolf/multi_agent/context_bus_v2.py'], 'tests': ['python3 -m multi_agent.context_bus_v2 --test']},
            173: {'files': ['/home/adem/graywolf/multi_agent/conflict_resolver.py'], 'tests': ['python3 -m multi_agent.conflict_resolver --test']},
            174: {'files': ['/home/adem/graywolf/multi_agent/parallel_guard.py'], 'tests': ['python3 -m multi_agent.parallel_guard --test']},
            175: {'files': ['/home/adem/graywolf/multi_agent/guardrails.py'], 'tests': ['python3 -m multi_agent.guardrails --test']},
            176: {'files': ['/home/adem/graywolf/multi_agent/evidence_merge.py'], 'tests': ['python3 -m multi_agent.evidence_merge --test']},
            177: {'files': ['/home/adem/graywolf/multi_agent/failure_analysis.py'], 'tests': ['python3 -m multi_agent.failure_analysis --test']},
            178: {'files': ['/home/adem/graywolf/multi_agent/rollback_arbitration.py'], 'tests': ['python3 -m multi_agent.rollback_arbitration --test']},
            179: {'files': ['/home/adem/graywolf/multi_agent/fleet_dispatch.py'], 'tests': ['python3 -m multi_agent.fleet_dispatch --test']},
            180: {'files': ['/home/adem/graywolf/multi_agent/certification.py'], 'tests': ['python3 -m multi_agent.certification --test']},

            181: {'files': ['/home/adem/graywolf/goals/goal_interface.py'], 'tests': ['python3 -m goals.goal_interface --test']},
            182: {'files': ['/home/adem/graywolf/goals/goal_router.py'], 'tests': ['python3 -m goals.goal_router --test']},
            183: {'files': ['/home/adem/graywolf/capabilities/registry.py'], 'tests': ['python3 -m capabilities.registry --test']},
            184: {'files': ['/home/adem/graywolf/tools/discovery_engine.py'], 'tests': ['python3 -m tools.discovery_engine --test']},
            185: {'files': ['/home/adem/graywolf/tools/tool_guard.py'], 'tests': ['python3 -m tools.tool_guard --test']},
            186: {'files': ['/home/adem/graywolf/coding/code_structure_analyzer.py'], 'tests': ['python3 -m coding.code_structure_analyzer --test']},
            187: {'files': ['/home/adem/graywolf/coding/semantic_search.py'], 'tests': ['python3 -m coding.semantic_search --test']},
            188: {'files': ['/home/adem/graywolf/coding/auto_bugfixer.py'], 'tests': ['python3 -m coding.auto_bugfixer --test']},
            189: {'files': ['/home/adem/graywolf/coding/refactor_engine.py'], 'tests': ['python3 -m coding.refactor_engine --test']},
            190: {'files': ['/home/adem/graywolf/coding/certification.py'], 'tests': ['python3 -m coding.certification --test']},
            191: {'files': ['/home/adem/graywolf/infra/state_mapper.py'], 'tests': ['python3 -m infra.state_mapper --test']},
            192: {'files': ['/home/adem/graywolf/infra/service_graph.py'], 'tests': ['python3 -m infra.service_graph --test']},
            193: {'files': ['/home/adem/graywolf/infra/incident_response.py'], 'tests': ['python3 -m infra.incident_response --test']},
            194: {'files': ['/home/adem/graywolf/infra/deploy_strategy.py'], 'tests': ['python3 -m infra.deploy_strategy --test']},
            195: {'files': ['/home/adem/graywolf/infra/optimization_ai.py'], 'tests': ['python3 -m infra.optimization_ai --test']},
            196: {'files': ['/home/adem/graywolf/research/knowledge_graph.py'], 'tests': ['python3 -m research.knowledge_graph --test']},
            197: {'files': ['/home/adem/graywolf/research/document_intel.py'], 'tests': ['python3 -m research.document_intel --test']},
            198: {'files': ['/home/adem/graywolf/research/pattern_mining.py'], 'tests': ['python3 -m research.pattern_mining --test']},
            199: {'files': ['/home/adem/graywolf/research/strategy_generator.py'], 'tests': ['python3 -m research.strategy_generator --test']},
            200: {'files': ['/home/adem/graywolf/research/certification.py'], 'tests': ['python3 -m research.certification --test']},
            201: {'files': ['/home/adem/graywolf/ai/architecture_analyzer.py'], 'tests': ['python3 -m ai.architecture_analyzer --test']},
            202: {'files': ['/home/adem/graywolf/ai/bottleneck_detector.py'], 'tests': ['python3 -m ai.bottleneck_detector --test']},
            203: {'files': ['/home/adem/graywolf/ai/self_patch_proposal.py'], 'tests': ['python3 -m ai.self_patch_proposal --test']},
            204: {'files': ['/home/adem/graywolf/ai/sandbox_evolution.py'], 'tests': ['python3 -m ai.sandbox_evolution --test']},
            205: {'files': ['/home/adem/graywolf/ai/evolution_approval.py'], 'tests': ['python3 -m ai.evolution_approval --test']},
            206: {'files': ['/home/adem/graywolf/ai/external_adapter.py'], 'tests': ['python3 -m ai.external_adapter --test']},
            207: {'files': ['/home/adem/graywolf/ai/api_intelligence.py'], 'tests': ['python3 -m ai.api_intelligence --test']},
            208: {'files': ['/home/adem/graywolf/ai/data_pipeline.py'], 'tests': ['python3 -m ai.data_pipeline --test']},
            209: {'files': ['/home/adem/graywolf/ai/workflow_generator.py'], 'tests': ['python3 -m ai.workflow_generator --test']},
            210: {'files': ['/home/adem/graywolf/ai/cross_system_cert.py'], 'tests': ['python3 -m ai.cross_system_cert --test']},
            211: {'files': ['/home/adem/graywolf/ai/global_context.py'], 'tests': ['python3 -m ai.global_context --test']},
            212: {'files': ['/home/adem/graywolf/ai/strategic_planning.py'], 'tests': ['python3 -m ai.strategic_planning --test']},
            213: {'files': ['/home/adem/graywolf/ai/resource_allocation.py'], 'tests': ['python3 -m ai.resource_allocation --test']},
            214: {'files': ['/home/adem/graywolf/ai/risk_modeling.py'], 'tests': ['python3 -m ai.risk_modeling --test']},
            215: {'files': ['/home/adem/graywolf/ai/decision_governance.py'], 'tests': ['python3 -m ai.decision_governance --test']},
            216: {'files': ['/home/adem/graywolf/ai/mission_system.py'], 'tests': ['python3 -m ai.mission_system --test']},
            217: {'files': ['/home/adem/graywolf/ai/self_monitoring_v2.py'], 'tests': ['python3 -m ai.self_monitoring_v2 --test']},
            218: {'files': ['/home/adem/graywolf/ai/autonomous_recovery_v2.py'], 'tests': ['python3 -m ai.autonomous_recovery_v2 --test']},
            219: {'files': ['/home/adem/graywolf/ai/global_optimization_loop.py'], 'tests': ['python3 -m ai.global_optimization_loop --test']},
            220: {'files': ['/home/adem/graywolf/ai/os_certification.py'], 'tests': ['python3 -m ai.os_certification --test']},
        }

        plan = plans.get(phase_no, {'files': [], 'tests': []})
        files = plan.get('files', [])
        tests = plan.get('tests', [])

        compile_cmd = ''
        if files:
            compile_cmd = 'python3 -m py_compile ' + ' '.join(files)

        commands = []
        if compile_cmd:
            commands.append(compile_cmd)
        commands.extend(tests)

        return {'files': files, 'tests': tests, 'commands': commands}

    def _artifact_complete(self, milestone: str) -> bool:
        req = self._requirements(milestone)
        files = req.get('files', [])
        if not files:
            return False
        return all(Path(f).exists() for f in files)

    def _parse_roadmap_phases(self) -> list[str]:
        text = ROADMAP.read_text(encoding='utf-8') if ROADMAP.exists() else ''
        matches = re.findall(r'^##\s+(Phase\s+(\d+)\s+[—–-]\s+.+)$', text, flags=re.MULTILINE)
        matches.sort(key=lambda t: int(t[1]))
        return [m[0] for m in matches]

    def discover_next_task(self) -> dict:
        phases = self._parse_roadmap_phases()
        st = self._load_state()
        completed_raw = st.get('completed', [])
        completed_norm = {normalize_milestone(x) for x in completed_raw}

        # remove stale completions if artifact gate fails
        adjusted = []
        for c in completed_raw:
            if c.startswith('Phase 8') and not self._artifact_complete(c):
                continue
            adjusted.append(c)
        if adjusted != completed_raw:
            st['completed'] = adjusted
            completed_norm = {normalize_milestone(x) for x in adjusted}
            self._save_state(st)

        candidates = []
        for m in phases:
            if '✅' in m:
                continue
            m_norm = normalize_milestone(m)
            if m_norm in completed_norm:
                continue
            candidates.append((m, m_norm))

        if not candidates:
            # idle-seed: if roadmap has no incomplete phases, append next ops-cycle phases (221+)
            try:
                seed_next_batch_if_idle(batch_size=5)
            except Exception:
                pass
            phases = self._parse_roadmap_phases()
            candidates = []
            for m in phases:
                if '✅' in m:
                    continue
                m_norm = normalize_milestone(m)
                if m_norm in completed_norm:
                    continue
                candidates.append((m, m_norm))
            if not candidates:
                return {'milestone': None, 'reason': 'no_incomplete_milestone'}

        selected, selected_norm = candidates[0]
        last_norm = st.get('last_selected_norm')
        if selected_norm == last_norm and selected_norm in completed_norm:
            if len(candidates) > 1:
                selected, selected_norm = candidates[1]
            else:
                return {
                    'milestone': None,
                    'reason': 'no_progress',
                    'selected_milestone': selected,
                    'state_snapshot': st,
                    'parsed_milestones': phases,
                }

        return {'milestone': selected}

    def _files_exist(self, files: list[str]) -> dict:
        missing = [f for f in files if not Path(f).exists()]
        return {'ok': len(missing) == 0, 'missing': missing}

    def _auto_build_phase8(self, missing: list[str]):
        # minimal safe writer for required files
        for f in missing:
            Path(f).parent.mkdir(parents=True, exist_ok=True)
            if f.endswith('branch_executor.py'):
                Path(f).write_text(
                    "import argparse, json\n"
                    "def execute_branch(workflow, context):\n"
                    "    branches = workflow.get('branches', [])\n"
                    "    default = workflow.get('default', {'name':'default_path'})\n"
                    "    for b in branches:\n"
                    "        if context.get(b.get('if_key')) == b.get('if_equals'): return {'status':'ok','selected':b.get('name')}\n"
                    "    return {'status':'ok','selected':default.get('name')}\n"
                    "def run_test():\n"
                    "    wf={'branches':[{'name':'premium_path','if_key':'tier','if_equals':'premium'}],'default':{'name':'default_path'}}\n"
                    "    a=execute_branch(wf, {'tier':'premium'})\n"
                    "    b=execute_branch(wf, {'tier':'x'})\n"
                    "    return {'status':'ok','premium_selected':a['selected']=='premium_path','default_selected':b['selected']=='default_path'}\n"
                    "if __name__=='__main__':\n"
                    "    p=argparse.ArgumentParser(); p.add_argument('--test', action='store_true'); args=p.parse_args(); print(json.dumps(run_test() if args.test else {'status':'idle'}, ensure_ascii=False))\n",
                    encoding='utf-8'
                )
            elif f.endswith('parallel_executor.py'):
                Path(f).write_text(
                    "import argparse, json, shlex, subprocess\n"
                    "from concurrent.futures import ThreadPoolExecutor\n"
                    "def _run(cmd):\n"
                    "    p=subprocess.run(shlex.split(cmd), capture_output=True, text=True, check=False)\n"
                    "    return {'exit_code':p.returncode}\n"
                    "def run_parallel(cmds, max_workers=2):\n"
                    "    with ThreadPoolExecutor(max_workers=max_workers) as ex: res=list(ex.map(_run, cmds))\n"
                    "    return {'status':'ok' if all(r['exit_code']==0 for r in res) else 'failed','results':res}\n"
                    "def run_test():\n"
                    "    out=run_parallel([\"python3 -c \\\"print(1)\\\"\",\"python3 -c \\\"print(2)\\\"\"])\n"
                    "    return {'status':out['status'],'all_zero':all(r['exit_code']==0 for r in out['results'])}\n"
                    "if __name__=='__main__':\n"
                    "    p=argparse.ArgumentParser(); p.add_argument('--test', action='store_true'); args=p.parse_args(); print(json.dumps(run_test() if args.test else {'status':'idle'}, ensure_ascii=False))\n",
                    encoding='utf-8'
                )
            elif f.endswith('compensation_handler.py'):
                Path(f).write_text(
                    "import argparse, json\n"
                    "def execute_with_compensation(steps):\n"
                    "    marks=[]\n"
                    "    comps=[]\n"
                    "    for s in steps:\n"
                    "        if s.get('fail'):\n"
                    "            for c in reversed(comps): c(marks)\n"
                    "            return {'status':'compensated','marks':marks}\n"
                    "        if s.get('compensate'): comps.append(s['compensate'])\n"
                    "    return {'status':'completed','marks':marks}\n"
                    "def run_test():\n"
                    "    def c1(m): m.append('undo_s1')\n"
                    "    def c2(m): m.append('undo_s2')\n"
                    "    out=execute_with_compensation([{'compensate':c1},{'compensate':c2},{'fail':True}])\n"
                    "    return {'status':out['status'],'compensated_order_ok':out['marks']==['undo_s2','undo_s1']}\n"
                    "if __name__=='__main__':\n"
                    "    p=argparse.ArgumentParser(); p.add_argument('--test', action='store_true'); args=p.parse_args(); print(json.dumps(run_test() if args.test else {'status':'idle'}, ensure_ascii=False))\n",
                    encoding='utf-8'
                )

    def _run_tests(self, tests: list[str]) -> dict:
        results = []
        ok_all = True
        for cmd in tests:
            out = self.tool.run_command(cmd)
            ok = out.get('status') == 'success' and int(out.get('log', {}).get('exit_code', 1)) == 0
            results.append({'cmd': cmd, 'ok': ok})
            if not ok:
                ok_all = False
        return {'ok': ok_all, 'results': results}

    def verify_logs(self) -> dict:
        if not LOG_PATH.exists():
            return {'status': 'error', 'error': 'log_missing'}
        return {'status': 'ok', 'tail': LOG_PATH.read_text(encoding='utf-8').splitlines()[-5:]}

    def mark_complete(self, milestone: str):
        st = self._load_state()
        if st.get('last_result') != 'verified':
            return {'status': 'blocked', 'reason': 'verification_flag_missing', 'milestone': milestone}
        completed = st.get('completed', [])
        if milestone not in completed:
            completed.append(milestone)
        st['completed'] = completed
        st['last_selected'] = milestone
        st['last_selected_norm'] = normalize_milestone(milestone)
        st['last_run_ts'] = datetime.now(timezone.utc).isoformat()
        st['last_result'] = 'completed'
        self._save_state(st)
        return {'status': 'ok'}

    def _update_state_selection(self, milestone: str, result: str):
        st = self._load_state()
        st['last_selected'] = milestone
        st['last_selected_norm'] = normalize_milestone(milestone)
        st['last_run_ts'] = datetime.now(timezone.utc).isoformat()
        st['last_result'] = result
        self._save_state(st)

    def cycle(self) -> dict:
        discovery = self.discover_next_task()
        milestone = discovery.get('milestone')
        if not milestone:
            return {'status': 'blocked', **discovery} if discovery.get('reason') == 'no_progress' else {'status': 'idle', **discovery}

        req = self._requirements(milestone)

        if self.dry_run:
            self._update_state_selection(milestone, 'dry_run')
            return {
                'status': 'dry_run',
                'milestone': milestone,
                'planned_actions': {
                    'required_files': req.get('files', []),
                    'required_tests': req.get('tests', []),
                    'required_commands': req.get('commands', []),
                },
            }

        files = self._files_exist(req['files'])
        if not files['ok'] and milestone.startswith('Phase 8'):
            self._auto_build_phase8(files['missing'])
            files = self._files_exist(req['files'])
        if not files['ok']:
            self._update_state_selection(milestone, 'blocked_missing_files')
            return {'status': 'blocked', 'milestone': milestone, 'reason': 'missing_files', 'missing': files['missing']}

        commands = req.get('commands', [])
        if not commands:
            self._update_state_selection(milestone, 'blocked_verification_plan_missing')
            return {'status': 'blocked', 'milestone': milestone, 'reason': 'verification_plan_missing'}

        cmd_results = []
        all_ok = True
        for cmd in commands:
            out = self.tool.run_command(cmd)
            ok = out.get('status') == 'success' and int(out.get('log', {}).get('exit_code', 1)) == 0
            cmd_results.append({'cmd': cmd, 'ok': ok})
            if not ok:
                all_ok = False

        logs = self.verify_logs()

        if all_ok and logs.get('status') == 'ok':
            self._update_state_selection(milestone, 'verified')
            mk = self.mark_complete(milestone)
            if mk.get('status') != 'ok':
                return {'status': 'blocked', 'milestone': milestone, 'reason': mk.get('reason', 'verification_gate_failed')}
            return {'status': 'completed', 'milestone': milestone, 'verification': cmd_results}

        self._update_state_selection(milestone, 'blocked_verification_failed')
        return {'status': 'blocked', 'milestone': milestone, 'reason': 'verification_failed', 'verification': cmd_results, 'log': logs}


def main():
    p = argparse.ArgumentParser(description='GrayWolf autonomous execution loop')
    p.add_argument('--interval', type=int, default=60)
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--once', action='store_true')
    args = p.parse_args()

    loop = AgentLoop(dry_run=args.dry_run)
    while True:
        out = loop.cycle()
        print(json.dumps(out, ensure_ascii=False))
        if args.once or args.dry_run:
            break
        time.sleep(args.interval)


if __name__ == '__main__':
    main()
