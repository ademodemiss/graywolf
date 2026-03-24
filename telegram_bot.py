#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import json
import os
import subprocess
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

ROOT = Path(__file__).resolve().parent
GRAYWOLF = ROOT / "scripts" / "graywolf"
MAX_TG = 4000
RUN_TIMEOUT = 180


def split_chunks(text: str, limit: int = MAX_TG) -> list[str]:
    text = (text or "").strip()
    if not text:
        return ["(çıktı yok)"]
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + limit, len(text))
        chunk = text[start:end]
        if end < len(text):
            nl = chunk.rfind("\n")
            if nl > 200:
                chunk = chunk[:nl]
                end = start + nl
        chunk = chunk.strip()
        if chunk:
            chunks.append(chunk)
        start = end

    return chunks or ["(çıktı yok)"]


def _run_graywolf(args: list[str]) -> dict:
    cmd = [str(GRAYWOLF), *args]
    p = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=RUN_TIMEOUT)
    stdout = (p.stdout or "").strip()
    stderr = (p.stderr or "").strip()

    parsed = None
    if stdout:
        try:
            parsed = json.loads(stdout.splitlines()[-1])
        except Exception:
            parsed = None

    return {
        "cmd": " ".join(cmd),
        "exit_code": p.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "json": parsed,
    }


def _sanitize_for_telegram(text: str) -> str:
    t = (text or '').replace('\r\n', '\n').replace('\r', '\n')
    # Telegram görünümünü bozabilecek kontrol karakterlerini temizle (newline/tab hariç)
    t = ''.join(ch for ch in t if ch == '\n' or ch == '\t' or ord(ch) >= 32)
    return t.strip()


def _format_result(res: dict) -> str:
    js = res.get("json") if isinstance(res, dict) else None
    if isinstance(js, dict):
        status = js.get("status", "unknown")
        command = js.get("command", "unknown")
        mode = js.get("mode")
        triage = js.get("triage") if isinstance(js.get("triage"), dict) else {}
        summary = (((js.get("ux") or {}).get("summary")) if isinstance(js.get("ux"), dict) else None) or ""
        next_step = (((js.get("ux") or {}).get("next_step")) if isinstance(js.get("ux"), dict) else None) or ""
        final = js.get("final") if isinstance(js.get("final"), dict) else {}
        reason = final.get("reason") or ""
        classification = final.get("classification") or ""

        lines = [f"status: {status}", f"command: {command}"]
        if mode:
            lines.append(f"mode: {mode}")
        if triage.get("kind"):
            lines.append(f"triage: {triage.get('kind')} ({triage.get('reason', 'n/a')})")
        if summary:
            lines.append(f"summary: {summary}")
        if next_step:
            lines.append(f"next_step: {next_step}")
        if classification:
            lines.append(f"classification: {classification}")
        if reason:
            lines.append(f"reason: {reason}")

        errors = js.get("errors") if isinstance(js.get("errors"), list) else []
        if errors:
            lines.append(f"errors: {', '.join(str(x) for x in errors[:5])}")

        if js.get("run_id"):
            lines.append(f"run_id: {js['run_id']}")
        if js.get("pause") and isinstance(js["pause"], dict):
            apr = js["pause"].get("approval_request_id")
            if apr:
                lines.append(f"approval_request_id: {apr}")

        return _sanitize_for_telegram("\n".join(lines))

    out = res.get("stdout") or res.get("stderr") or "(çıktı yok)"
    out = _sanitize_for_telegram(out)
    return out or "(çıktı yok)"


async def _reply_long(update: Update, text: str) -> None:
    for chunk in split_chunks(text):
        await update.effective_message.reply_text(chunk)


async def cmd_run(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = " ".join(context.args).strip()
    if not msg:
        await update.effective_message.reply_text("Kullanım: /run <mesaj>")
        return
    try:
        res = _run_graywolf(["assistant", "--message", msg])
        await _reply_long(update, _format_result(res))
    except Exception as e:
        await update.effective_message.reply_text(f"Hata: assistant çalıştırılamadı ({e})")


async def cmd_plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = " ".join(context.args).strip()
    if not msg:
        await update.effective_message.reply_text("Kullanım: /plan <mesaj>")
        return
    try:
        res = _run_graywolf(["assistant", "--message", msg, "--plan-only"])
        await _reply_long(update, _format_result(res))
    except Exception as e:
        await update.effective_message.reply_text(f"Hata: plan çalıştırılamadı ({e})")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        res = _run_graywolf(["status"])
        await _reply_long(update, _format_result(res))
    except Exception as e:
        await update.effective_message.reply_text(f"Hata: status alınamadı ({e})")


async def cmd_approvals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        res = _run_graywolf(["approvals"])
        await _reply_long(update, _format_result(res))
    except Exception as e:
        await update.effective_message.reply_text(f"Hata: approvals alınamadı ({e})")


async def cmd_approve(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    req_id = " ".join(context.args).strip()
    if not req_id:
        await update.effective_message.reply_text("Kullanım: /approve <request_id>")
        return
    try:
        res = _run_graywolf(["approve", req_id])
        await _reply_long(update, _format_result(res))
    except Exception as e:
        await update.effective_message.reply_text(f"Hata: approve çalıştırılamadı ({e})")


async def plain_text_as_run(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (update.effective_message.text or "").strip()
    if not text:
        return
    try:
        res = _run_graywolf(["assistant", "--message", text])
        await _reply_long(update, _format_result(res))
    except Exception as e:
        await update.effective_message.reply_text(f"Hata: mesaj işlenemedi ({e})")


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN environment variable gerekli")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("run", cmd_run))
    app.add_handler(CommandHandler("plan", cmd_plan))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("approvals", cmd_approvals))
    app.add_handler(CommandHandler("approve", cmd_approve))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, plain_text_as_run))

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
