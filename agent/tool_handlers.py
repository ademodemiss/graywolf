import datetime
import json
import os
from pathlib import Path

from tools.file_tool import FileTool

try:
    from tools.excel_tool import ExcelTool
except ImportError:  # excused if openpyxl not installed yet
    ExcelTool = None


class FileHandler:
    def __init__(self, base_dir: str = "/home/adem/graywolf"):
        self.tool = FileTool(base_dir=base_dir)

    def execute(self, step: dict) -> dict:
        desc = (step.get("description") or "").lower()
        if "read" in desc or "okuma" in desc:
            file_path = "planning/agent_first_plan.md"
            result = self.tool.read(file_path)
            summary = f"read {file_path}"
        elif "write" in desc or "oluştur" in desc:
            file_path = "planning/phaseA_dispatch_log.md"
            content = "Dispatch log entry: " + datetime.datetime.utcnow().isoformat() + "\n"
            result = self.tool.write(file_path, content)
            summary = f"write {file_path}"
        else:
            result = self.tool.list(".")
            summary = "list repo"

        return {
            "status": result["status"],
            "tool": "file_tool",
            "description": desc,
            "action": summary,
            "result": result,
            "step_id": step.get("id"),
        }


class SimpleCodeGenerator:
    def generate(self, requirement: str, language: str = "python") -> str:
        safe_requirement = requirement.replace("'", "\\'")
        template = (
            "# Otomatik oluşturulmuş çözüm\n"
            f"def solution():\n    print('{safe_requirement}')\n"
        )
        return template


class CodeHandler:
    def __init__(self):
        self.generator = SimpleCodeGenerator()

    def execute(self, step: dict) -> dict:
        requirement = step.get("description") or "Kod üretimi"
        code = self.generator.generate(requirement)
        return {
            "status": "success",
            "tool": "code_tool",
            "description": requirement,
            "code_snippet": code,
            "analysis": "Çıktı sadece örnek şablondur.",
            "step_id": step.get("id"),
        }


class ExcelHandler:
    def __init__(self, workspace_dir: str = "/home/adem/graywolf"):
        self.workspace_dir = Path(workspace_dir)
        if ExcelTool is None:
            self.tool = None
            self.fallback_path = self.workspace_dir / "data" / "dispatch_stub.xlsx"
            self.fallback_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            excel_file = self.workspace_dir / "data" / "dispatch_sheet.xlsx"
            excel_file.parent.mkdir(parents=True, exist_ok=True)
            self.tool = ExcelTool(str(excel_file))

    def execute(self, step: dict) -> dict:
        sheet = "dispatch"
        if self.tool:
            try:
                self.tool.write_sheet(sheet, [["dispatch_time", datetime.datetime.utcnow().isoformat()]], overwrite=False)
                status = "success"
            except Exception as e:
                status = f"error: {e}"
        else:
            with open(self.fallback_path, "a", encoding="utf-8") as f:
                f.write(datetime.datetime.utcnow().isoformat() + " - fallback excel entry\n")
            status = "fallback written"

        return {
            "status": status,
            "tool": "excel_tool",
            "description": step.get("description"),
            "sheet": sheet,
            "step_id": step.get("id"),
        }


class MailHandler:
    def __init__(self, log_dir: str = "/home/adem/graywolf/logs"):
        self.log_path = Path(log_dir) / "dispatcher_mail.log"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def execute(self, step: dict) -> dict:
        payload = {
            "subject": "Dispatcher mail",
            "body": step.get("description"),
            "timestamp": datetime.datetime.utcnow().isoformat(),
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
        return {
            "status": "queued",
            "tool": "mail_tool",
            "description": step.get("description"),
            "queued_to": "ops@example.com",
            "step_id": step.get("id"),
        }


class ReportHandler:
    def __init__(self, log_dir: str = "/home/adem/graywolf/logs"):
        self.log_path = Path(log_dir) / "dispatcher_report.log"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def execute(self, step: dict) -> dict:
        payload = {
            "report": step.get("description"),
            "timestamp": datetime.datetime.utcnow().isoformat(),
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
        return {
            "status": "logged",
            "tool": "report_tool",
            "description": step.get("description"),
            "step_id": step.get("id"),
        }
