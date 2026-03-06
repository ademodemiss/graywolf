from pathlib import Path


def normalize_paths(paths: list[str]) -> set[str]:
    out = set()
    for p in paths:
        if not p:
            continue
        out.add(str(Path(p)).replace('\\', '/'))
    return out


def classify_scope_violations(scope_files: list[str], staged: list[str], unstaged: list[str], untracked: list[str]) -> dict:
    scope = normalize_paths(scope_files)

    def outside(items: list[str]) -> list[str]:
        return [x for x in items if str(Path(x)).replace('\\', '/') not in scope]

    return {
        'scope_files': sorted(scope),
        'blocked_prestaged': outside(staged),
        'blocked_unstaged': outside(unstaged),
        'blocked_untracked': outside(untracked),
    }
