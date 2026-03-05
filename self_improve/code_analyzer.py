import ast
import json
from pathlib import Path


RISK_TOKENS = ["rm -rf", "shell=True", "subprocess.Popen(", "os.system("]


def _analyze_python_file(path: Path) -> dict:
    issues, suggestions, risks = [], [], []
    text = path.read_text(encoding="utf-8", errors="ignore")

    try:
        tree = ast.parse(text)
    except SyntaxError as e:
        issues.append(f"syntax_error:{path}:{e.lineno}:{e.msg}")
        risks.append("high")
        return {"issues": issues, "risk_level": risks, "suggestions": suggestions}

    imports = []
    used_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend([n.asname or n.name.split(".")[0] for n in node.names])
        elif isinstance(node, ast.ImportFrom):
            imports.extend([n.asname or n.name for n in node.names])
        elif isinstance(node, ast.Name):
            used_names.add(node.id)

    for name in imports:
        if name not in used_names:
            issues.append(f"unused_import:{path}:{name}")
            suggestions.append(f"remove unused import '{name}' in {path.name}")

    for token in RISK_TOKENS:
        if token in text:
            issues.append(f"risky_pattern:{path}:{token}")
            risks.append("medium")

    if "TODO" in text:
        suggestions.append(f"resolve TODO comments in {path.name}")

    return {"issues": issues, "risk_level": risks, "suggestions": suggestions}


def analyze_code(path: str = "/home/adem/graywolf") -> dict:
    base = Path(path)
    all_issues, all_risks, all_suggestions = [], [], []

    for py in base.rglob("*.py"):
        if "/venv/" in str(py):
            continue
        result = _analyze_python_file(py)
        all_issues.extend(result["issues"])
        all_risks.extend(result["risk_level"])
        all_suggestions.extend(result["suggestions"])

    # naive duplicate logic heuristic
    if len(all_issues) > 25:
        all_suggestions.append("consider refactoring repeated logic into shared helpers")

    return {
        "issues": all_issues,
        "risk_level": sorted(set(all_risks)) or ["low"],
        "suggestions": sorted(set(all_suggestions)),
    }


if __name__ == "__main__":
    print(json.dumps(analyze_code(), ensure_ascii=False))
