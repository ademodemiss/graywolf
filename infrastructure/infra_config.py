CONFIG = {
    'min_nodes': 1,
    'max_nodes': 10,
    'cpu_scale_up': 70,
    'cpu_scale_down': 25,
    'check_interval': 60,
}


def get_config() -> dict:
    return dict(CONFIG)
