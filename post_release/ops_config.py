import os
from dataclasses import dataclass, asdict


def _float_env(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return float(default)
    try:
        return float(raw)
    except ValueError:
        return float(default)


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return int(default)
    try:
        return int(raw)
    except ValueError:
        return int(default)


CPU_COUNT = os.cpu_count() or 1

OPS_LIMITS = {
    'DISK_WARN_PCT': _float_env('GW_DISK_WARN_PCT', 85),
    'DISK_ERROR_PCT': _float_env('GW_DISK_ERROR_PCT', 95),
    'LOAD_WARN': _float_env('GW_LOAD_WARN', CPU_COUNT * 1.5),
    'LOAD_ERROR': _float_env('GW_LOAD_ERROR', CPU_COUNT * 2.5),
    'TERMINAL_LOG_WARN_MB': _float_env('GW_LOG_WARN_MB', 50),
    'TERMINAL_LOG_ERROR_MB': _float_env('GW_LOG_ERROR_MB', 200),
}


@dataclass
class OpsConfig:
    disk_warn_pct: float = OPS_LIMITS['DISK_WARN_PCT']
    disk_error_pct: float = OPS_LIMITS['DISK_ERROR_PCT']
    load_warn: float = OPS_LIMITS['LOAD_WARN']
    load_error: float = OPS_LIMITS['LOAD_ERROR']
    log_warn_mb: float = OPS_LIMITS['TERMINAL_LOG_WARN_MB']
    log_error_mb: float = OPS_LIMITS['TERMINAL_LOG_ERROR_MB']


def load_config() -> OpsConfig:
    return OpsConfig()


def as_dict() -> dict:
    return asdict(load_config())
