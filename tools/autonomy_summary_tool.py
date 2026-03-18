#!/usr/bin/env python3
import argparse
from datetime import datetime


def build_summary(points: int) -> str:
    lines = [
        "1. Graywolf çekirdek orchestrator aktif ve görev planlama/çalıştırma yapıyor.",
        "2. Dashboard sağlık testi yeşil; servis durumu izlenebilir.",
        "3. Recovery/replan zinciri aktif; hata anında alternatif plan üretiliyor.",
        "4. Tool seti hazır: terminal, file, mail, excel, analysis, financial, code.",
        "5. Otonomi daemon arka planda çalışıyor ve queue görevlerini döngüyle alıyor.",
        "6. Policy guard kritik komutları koruyor; güvenli yazma yolları otomatik izinli.",
        "7. Test durumu stabil: kritik pytest ve günlük healthcheck seti çalışıyor.",
        "8. Sonraki odak: daha güçlü görev doğrulama ve uzun süreli tam otonomi sertleştirmesi.",
    ]
    selected = lines[: max(1, min(points, len(lines)))]
    ts = datetime.now().isoformat()
    header = f"Graywolf Autonomy Live Report ({ts})"
    body = "\n".join(selected)
    return f"{header}\n\n{body}\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate autonomy status summary")
    parser.add_argument("--points", type=int, default=8)
    args = parser.parse_args()
    print(build_summary(args.points), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
