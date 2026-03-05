import argparse
from pathlib import Path


def print_last_log_lines(path: str, n: int):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    for line in lines[-n:]:
        print(line)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GrayWolf report helper")
    parser.add_argument("--last-log", type=int, default=5)
    parser.add_argument("--path", default="/home/adem/graywolf/logs/terminal.log")
    args = parser.parse_args()
    print_last_log_lines(args.path, args.last_log)
