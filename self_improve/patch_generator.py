import json

from self_improve.improvement_engine import generate_improvement_plan


def generate_patch(path: str = "/home/adem/graywolf") -> dict:
    plan = generate_improvement_plan(path)
    first = plan["plan"][0] if plan.get("plan") else "no_action"
    risk_level = "low"
    if "risky" in first or "syntax" in first:
        risk_level = "medium"

    return {
        "file": "N/A",
        "change": first,
        "reason": "auto-generated from analyzer + improvement plan",
        "risk_level": risk_level,
    }


if __name__ == "__main__":
    print(json.dumps(generate_patch(), ensure_ascii=False))
