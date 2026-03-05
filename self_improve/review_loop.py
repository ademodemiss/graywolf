import json

from self_improve.patch_generator import generate_patch


DENY_TOKENS = ["rm -rf", "shell=True", "os.system("]


def review_patch(patch: dict) -> dict:
    payload = json.dumps(patch, ensure_ascii=False)
    for token in DENY_TOKENS:
        if token in payload:
            return {"status": "CONFIRM", "reason": f"dangerous token detected: {token}", "patch": patch}
    return {"status": "ALLOW", "reason": "no policy violation detected", "patch": patch}


def run_review(path: str = "/home/adem/graywolf") -> dict:
    patch = generate_patch(path)
    return review_patch(patch)


if __name__ == "__main__":
    print(json.dumps(run_review(), ensure_ascii=False))
