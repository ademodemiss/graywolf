"""Agent command parser: doğal dil isteğini araç planına çeviren prototip."""
import json
import re
from typing import Dict, List

PLAN_TEMPLATES = {
    "web": [
        "Araştırma: Proje amaçlarını belirle",
        "Terminal: Gerekli dizin yapısını oluştur",
        "FileTool: HTML/CSS/JS dosyalarını hazırla",
        "CodeTool: Basit bir servis template'i yaz",
        "Terminal: Gerekirse 'git init' + 'npm install' çalıştır",
    ],
    "data": [
        "ExcelTool: Veri kaynağını okur",
        "ExcelTool: Pivot/özet hesaplar",
        "ReportTool: Grafikleri hazırlar",
        "MailTool: İleri adımı bildirir",
    ],
    "deploy": [
        "Terminal: Durumu kontrol et (git status)",
        "Terminal: Testleri çalıştır",
        "Terminal: Deploy komutunu yürüte",
        "TelegramAlert: Sonucu raporla",
    ],
}

TOOL_KEYWORDS = {
    "terminal": ["terminal", "komut", "deploy", "git"],
    "file_tool": ["dosya", "klasör", "sil"],
    "code_tool": ["kod", "fonksiyon", "refactor"],
    "excel_tool": ["excel", "csv", "tablo", "veri"],
    "mail_tool": ["mail", "e-posta", "email"],
    "report_tool": ["rapor"],
}


def detect_plan_template(command: str) -> List[str]:
    lowered = command.lower()
    if any(keyword in lowered for keyword in ("web", "site", "app", "frontend")):
        return PLAN_TEMPLATES["web"]
    if any(keyword in lowered for keyword in ("excel", "csv", "tablo", "veri")):
        return PLAN_TEMPLATES["data"]
    if any(keyword in lowered for keyword in ("deploy", "yayın", "production", "sunucu")):
        return PLAN_TEMPLATES["deploy"]
    return [
        "Terminal: İsteği analiz et ve gerekli araçları hazırla",
        "FileTool: Gerekli dosya/dizin işlemlerini yap",
        "CodeTool: Kod/yapı değişikliklerini uygula",
        "MailTool: Gerekiyorsa kullanıcıyı bilgilendir",
    ]


def infer_tools(command: str) -> List[str]:
    lowered = command.lower()
    selected = set()
    for tool, keywords in TOOL_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            selected.add(tool)
    if not selected:
        selected.update(["terminal", "code_tool"])
    return sorted(selected)


def build_steps(template_steps: List[str]) -> List[Dict[str, str]]:
    steps = []
    for idx, step in enumerate(template_steps, start=1):
        match = re.match(r"(?P<tool>\w+): (?P<description>.+)", step)
        steps.append(
            {
                "id": f"step-{idx}",
                "tool": match.group("tool") if match else "terminal",
                "description": match.group("description") if match else step,
            }
        )
    return steps


def parse_command(command: str) -> Dict:
    template = detect_plan_template(command)
    inferred_tools = infer_tools(command)
    steps = build_steps(template)
    return {
        "objective": command,
        "tools": inferred_tools,
        "steps": steps,
        "plan_summary": " → ".join([step[step.index(":") + 2 :] if ":" in step else step for step in template]),
    }


if __name__ == "__main__":
    samples = [
        "Şirket sitesi yap ve deploy et",
        "Excel'deki satış tablosunu analiz et, grafik hazırla",
        "Sunucuda git pull yapıp testleri çalıştır",
    ]
    for sample in samples:
        plan = parse_command(sample)
        print(f"Komut: {sample}\nPlan:\n{json.dumps(plan, indent=2, ensure_ascii=False)}\n")
