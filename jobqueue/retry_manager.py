import time


def compute_backoff_seconds(attempt: int, base: float = 0.1, cap: float = 1.0) -> float:
    if attempt <= 1:
        return base
    value = base * (2 ** (attempt - 1))
    return cap if value > cap else value


def apply_backoff(attempt: int):
    time.sleep(compute_backoff_seconds(attempt))
