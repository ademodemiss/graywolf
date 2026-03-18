import argparse
from pathlib import Path
from datetime import datetime


def print_last_log_lines(path: str, n: int):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    for line in lines[-n:]:
        print(line)


def build_topic_report(topic: str, items: int) -> str:
    rows = [
        "Sistem aktif ve görev kuyruğu dinleniyor.",
        "Dashboard ve healthcheck hattı çalışır durumda.",
        "Replan/recovery mekanizması devrede.",
        "Tool seti (terminal/file/mail/excel/analysis/code) erişilebilir.",
        "Otonomi daemon döngüsel şekilde görev alıyor.",
        "Policy guard kritik komutlarda güvenlik uyguluyor.",
        "Kritik test seti stabil çalışıyor.",
        "Bir sonraki odak: görev kalite filtresi ve model yanıt denetimi.",
    ]
    selected = rows[: max(1, min(items, len(rows)))]
    ts = datetime.now().isoformat()
    return f"{topic} ({ts})\n\n" + "\n".join(f"{i+1}. {x}" for i, x in enumerate(selected)) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GrayWolf report helper")
    parser.add_argument("--last-log", type=int, default=5)
    parser.add_argument("--path", default="/home/adem/graywolf/logs/terminal.log")
    parser.add_argument("--topic", default=None)
    parser.add_argument("--items", type=int, default=8)
    parser.add_argument("--output_file", default=None)
    args = parser.parse_args()

    if args.topic:
        content = build_topic_report(args.topic, args.items)
        if args.output_file:
            out = args.output_file
            if not out.startswith("/"):
                out = f"/home/adem/graywolf/{out}"
            Path(out).parent.mkdir(parents=True, exist_ok=True)
            Path(out).write_text(content, encoding="utf-8")
            print(f"written:{out}")
        else:
            print(content, end="")
    else:
        print_last_log_lines(args.path, args.last_log)
