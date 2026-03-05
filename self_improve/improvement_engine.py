import json

from self_improve.code_analyzer import analyze_code


def generate_improvement_plan(path: str = "/home/adem/graywolf") -> dict:
    analysis = analyze_code(path)
    plan = []

    if any(i.startswith("syntax_error") for i in analysis["issues"]):
        plan.append("fix syntax errors first")
    if any(i.startswith("unused_import") for i in analysis["issues"]):
        plan.append("clean unused imports")
    if any(i.startswith("risky_pattern") for i in analysis["issues"]):
        plan.append("remove risky shell patterns and align with policy")
    if not plan:
        plan.append("no urgent issues; optimize logging and docs")

    return {"analysis_summary": {"issue_count": len(analysis["issues"]), "risk": analysis["risk_level"]}, "plan": plan}


if __name__ == "__main__":
    print(json.dumps(generate_improvement_plan(), ensure_ascii=False))
