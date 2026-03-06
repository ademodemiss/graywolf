import argparse
import json
from pathlib import Path

REPORT = Path('/home/adem/graywolf/reports/change_impact_report.json')


def analyze_impact(changed_files: list[str], repo_path: Path) -> dict:
    # This is a simplified simulation. In a real scenario, this would involve
    # static analysis, dependency graph traversal, and potentially dynamic tests.
    # For this phase, we'll simulate impact based on file patterns.

    impact_areas = set()
    related_tests = set()
    related_documentation = set()

    for file in changed_files:
        p = Path(file)
        if 'core/' in str(p):
            impact_areas.add('core_logic')
            related_tests.add('tests/test_core.py') # Example
            related_documentation.add('docs/core_architecture.md') # Example
        if 'ai/' in str(p):
            impact_areas.add('ai_models')
            related_tests.add('tests/test_ai.py')
            related_documentation.add('docs/ai_pipeline.md')
        if 'reports/' in str(p):
            impact_areas.add('reporting')
            related_tests.add('tests/test_reports.py')
            related_documentation.add('docs/reporting_guide.md')
        if 'policies/' in str(p):
            impact_areas.add('security_policy')
            related_tests.add('tests/test_policies.py')
            related_documentation.add('docs/security_policy.md')

    return {
        'changed_files': changed_files,
        'impact_areas': list(impact_areas),
        'suggested_tests': list(related_tests),
        'suggested_documentation': list(related_documentation),
        'severity': 'high' if 'core_logic' in impact_areas or len(impact_areas) > 2 else 'medium',
    }


def run_test() -> dict:
    # Simulate a scenario with changed files
    changed_files_scenario_1 = [
        'core/agent_loop.py',
        'ai/reasoning_trace.py',
    ]
    changed_files_scenario_2 = [
        'reports/real_task_cert_v2.py',
    ]

    impact_1 = analyze_impact(changed_files_scenario_1, Path('/home/adem/graywolf'))
    impact_2 = analyze_impact(changed_files_scenario_2, Path('/home/adem/graywolf'))

    out = {
        'status': 'ok',
        'scenarios': {
            'scenario_1': impact_1,
            'scenario_2': impact_2,
        },
        'checks': {
            'scenario_1_areas': sorted(impact_1['impact_areas']) == ['ai_models', 'core_logic'],
            'scenario_2_areas': sorted(impact_2['impact_areas']) == ['reporting'],
            'scenario_1_severity': impact_1['severity'] == 'high',
            'scenario_2_severity': impact_2['severity'] == 'medium', # reports change is medium
        }
    }
    REPORT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    out['artifact'] = str(REPORT)
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--test', action='store_true')
    a = p.parse_args()
    print(json.dumps(run_test() if a.test else {'status': 'idle'}, ensure_ascii=False))
