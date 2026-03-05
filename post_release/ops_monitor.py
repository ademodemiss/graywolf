import argparse
import json
import os
from pathlib import Path

from post_release.ops_config import load_config


def _status_by_threshold(value: float, warn: float, error: float) -> str:
    if value >= error:
        return 'error'
    if value >= warn:
        return 'warn'
    return 'ok'


def _disk_check(cfg) -> dict:
    st = os.statvfs('/')
    total = st.f_blocks * st.f_frsize
    free = st.f_bavail * st.f_frsize
    used_pct = 0.0 if total == 0 else ((total - free) / total) * 100.0
    status = _status_by_threshold(used_pct, cfg.disk_warn_pct, cfg.disk_error_pct)
    return {
        'name': 'disk_usage',
        'status': status,
        'value': round(used_pct, 2),
        'threshold': {'warn_pct': cfg.disk_warn_pct, 'error_pct': cfg.disk_error_pct},
        'details': {'path': '/'},
    }


def _load_check(cfg) -> dict:
    try:
        load1, _, _ = os.getloadavg()
    except Exception:
        load1 = 0.0
    status = _status_by_threshold(load1, cfg.load_warn, cfg.load_error)
    return {
        'name': 'loadavg_1m',
        'status': status,
        'value': round(load1, 3),
        'threshold': {'warn': cfg.load_warn, 'error': cfg.load_error},
        'details': {'cpu_count': os.cpu_count() or 1},
    }


def _log_size_check(cfg) -> dict:
    p = Path('/home/adem/graywolf/logs/terminal.log')
    size_mb = (p.stat().st_size / (1024 * 1024)) if p.exists() else 0.0
    status = _status_by_threshold(size_mb, cfg.log_warn_mb, cfg.log_error_mb)
    return {
        'name': 'terminal_log_size_mb',
        'status': status,
        'value': round(size_mb, 3),
        'threshold': {'warn_mb': cfg.log_warn_mb, 'error_mb': cfg.log_error_mb},
        'details': {'path': str(p), 'exists': p.exists()},
    }


def _memory_check() -> dict:
    used_pct = None
    detail = {}
    try:
        import psutil  # type: ignore

        vm = psutil.virtual_memory()
        used_pct = float(vm.percent)
        detail = {'source': 'psutil', 'total': int(vm.total), 'available': int(vm.available)}
    except Exception:
        meminfo = Path('/proc/meminfo')
        if meminfo.exists():
            vals = {}
            for line in meminfo.read_text(encoding='utf-8').splitlines():
                parts = line.split(':', 1)
                if len(parts) != 2:
                    continue
                key = parts[0].strip()
                num = parts[1].strip().split()[0]
                if num.isdigit():
                    vals[key] = int(num)  # kB
            total = vals.get('MemTotal', 0)
            avail = vals.get('MemAvailable', vals.get('MemFree', 0))
            if total > 0:
                used_pct = ((total - avail) / total) * 100.0
                detail = {'source': '/proc/meminfo', 'total_kb': total, 'available_kb': avail}

    if used_pct is None:
        return {
            'name': 'memory_usage',
            'status': 'warn',
            'value': None,
            'threshold': {'warn_pct': 85, 'error_pct': 95},
            'details': {'reason': 'memory_probe_unavailable'},
        }

    status = _status_by_threshold(used_pct, 85, 95)
    return {
        'name': 'memory_usage',
        'status': status,
        'value': round(used_pct, 2),
        'threshold': {'warn_pct': 85, 'error_pct': 95},
        'details': detail,
    }


def run_monitor() -> dict:
    cfg = load_config()
    checks = [
        _disk_check(cfg),
        _load_check(cfg),
        _log_size_check(cfg),
        _memory_check(),
    ]
    statuses = [c['status'] for c in checks]
    if 'error' in statuses:
        overall = 'error'
    elif 'warn' in statuses:
        overall = 'warn'
    else:
        overall = 'ok'
    return {'status': overall, 'checks': checks}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--test', action='store_true')
    args = p.parse_args()
    out = run_monitor() if args.test else {'status': 'idle'}
    print(json.dumps(out, ensure_ascii=False))
