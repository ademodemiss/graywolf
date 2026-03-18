"""Agent task decomposer: plan adımlarını tool çağrılarına eşler."""
from __future__ import annotations

from typing import Dict, List

from agent.command_parser import parse_command

TOOL_SYNONYMS = {
    "terminal": "terminal",
    "terminaltool": "terminal",
    "filetool": "file_tool",
    "file": "file_tool",
    "codetool": "code_tool",
    "code": "code_tool",
    "exceltool": "excel_tool",
    "excel": "excel_tool",
    "mailtool": "mail_tool",
    "mail": "mail_tool",
    "reporttool": "report_tool",
    "telegramalert": "telegram_alert",
    "research": "terminal",
}


def _normalize_tool(tool_label: str) -> str:
    key = tool_label.lower().replace(" ", "")
    return TOOL_SYNONYMS.get(key, "terminal")


def decompose_plan(command: str | None = None, plan: Dict | None = None) -> List[Dict]:
    """Planı decomposer ederek çalıştırılabilir adımlar üretir."""
    if plan is None:
        if command is None:
            raise ValueError("Komut veya plan olmadan decomposition yapılamaz.")
        plan = parse_command(command)

    steps = []
    for raw_step in plan["steps"]:
        tool_key = _normalize_tool(raw_step.get("tool", "terminal"))
        steps.append(
            {
                "id": raw_step.get("id"),
                "tool": tool_key,
                "description": raw_step.get("description"),
                "raw_step": raw_step,
            }
        )
    return steps


def plan_summary_from_command(command: str) -> Dict:
    plan = parse_command(command)
    return {
        "plan": plan,
        "decomposed_steps": decompose_plan(plan=plan),
    }
