import argparse
import base64
import datetime
import json
import os
import smtplib
from dataclasses import asdict, dataclass
from email.message import EmailMessage

try:
    from tools.provider_validation import validate_provider_env
except ModuleNotFoundError:
    from provider_validation import validate_provider_env


@dataclass
class MailDraft:
    to: str
    subject: str
    body: str
    created_at: str
    status: str = "draft"


class MailTool:
    REQUIRED_SMTP_ENV_BASIC = ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS", "SMTP_FROM"]
    REQUIRED_SMTP_ENV_OAUTH2 = ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_FROM", "SMTP_OAUTH2_TOKEN"]

    def __init__(self, draft_dir: str = "/home/adem/graywolf/memory/mail_drafts"):
        self.draft_dir = draft_dir
        os.makedirs(self.draft_dir, exist_ok=True)

    def _draft_path(self, draft_id: str) -> str:
        return os.path.join(self.draft_dir, f"{draft_id}.json")

    def _resolve_smtp(self, smtp_cfg: dict | None = None) -> tuple[dict, list[str]]:
        smtp_cfg = smtp_cfg or {}
        auth_method = (smtp_cfg.get("auth_method") or os.getenv("SMTP_AUTH_METHOD", "basic")).strip().lower()

        smtp_host = smtp_cfg.get("host") or os.getenv("SMTP_HOST", "")
        smtp_port_raw = smtp_cfg.get("port") or os.getenv("SMTP_PORT", "")
        smtp_user = smtp_cfg.get("user") or os.getenv("SMTP_USER", "")
        smtp_pass = smtp_cfg.get("password") or os.getenv("SMTP_PASS", "")
        smtp_oauth2_token = smtp_cfg.get("oauth2_token") or os.getenv("SMTP_OAUTH2_TOKEN", "")
        smtp_from = smtp_cfg.get("from_addr") or os.getenv("SMTP_FROM", smtp_user)

        missing = []
        if not smtp_host:
            missing.append("SMTP_HOST")
        if not smtp_port_raw:
            missing.append("SMTP_PORT")
        if not smtp_user:
            missing.append("SMTP_USER")
        if not smtp_from:
            missing.append("SMTP_FROM")

        if auth_method == "oauth2":
            if not smtp_oauth2_token:
                missing.append("SMTP_OAUTH2_TOKEN")
        else:
            if not smtp_pass:
                missing.append("SMTP_PASS")

        try:
            smtp_port = int(str(smtp_port_raw))
        except (TypeError, ValueError):
            smtp_port = 587
            if "SMTP_PORT" not in missing:
                missing.append("SMTP_PORT")

        cfg = {
            "host": smtp_host,
            "port": smtp_port,
            "user": smtp_user,
            "password": smtp_pass,
            "oauth2_token": smtp_oauth2_token,
            "from_addr": smtp_from,
            "auth_method": auth_method,
        }
        return cfg, missing

    def create_draft(self, to: str, subject: str, body: str) -> dict:
        draft = MailDraft(
            to=to,
            subject=subject,
            body=body,
            created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        )
        draft_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        path = self._draft_path(draft_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(draft), f, ensure_ascii=False, indent=2)
        return {"status": "draft_created", "draft_id": draft_id, "path": path}

    def confirm_draft(self, draft_id: str, approved: bool) -> dict:
        path = self._draft_path(draft_id)
        if not os.path.exists(path):
            return {"status": "error", "error": "draft_not_found", "draft_id": draft_id}

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["status"] = "approved" if approved else "rejected"
        data["confirmed_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return {
            "status": "draft_confirmed",
            "draft_id": draft_id,
            "approved": approved,
            "path": path,
        }

    def _smtp_auth(self, server: smtplib.SMTP, cfg: dict):
        auth_method = cfg.get("auth_method", "basic")
        if auth_method == "oauth2":
            auth_string = f"user={cfg['user']}\x01auth=Bearer {cfg['oauth2_token']}\x01\x01"
            encoded = base64.b64encode(auth_string.encode("utf-8")).decode("ascii")
            code, resp = server.docmd("AUTH", "XOAUTH2 " + encoded)
            if code != 235:
                raise RuntimeError(f"smtp_oauth2_auth_failed code={code} resp={resp}")
            return

        server.login(cfg["user"], cfg["password"])

    def test_smtp(self, smtp_cfg: dict | None = None) -> dict:
        cfg, missing = self._resolve_smtp(smtp_cfg)
        if missing:
            return {
                "status": "warning",
                "warning": "missing_smtp_env",
                "missing": missing,
                "fallback": "dry_run",
                "auth_method": cfg.get("auth_method", "basic"),
            }

        try:
            with smtplib.SMTP(cfg["host"], cfg["port"], timeout=20) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                self._smtp_auth(server, cfg)
            return {
                "status": "ok",
                "smtp": "connection_and_auth_success",
                "auth_method": cfg.get("auth_method", "basic"),
            }
        except Exception as e:
            return {
                "status": "error",
                "error": "smtp_connection_failed",
                "detail": str(e),
                "auth_method": cfg.get("auth_method", "basic"),
            }

    def send_draft(self, draft_id: str, dry_run: bool = True, smtp_cfg: dict | None = None) -> dict:
        path = self._draft_path(draft_id)
        if not os.path.exists(path):
            return {"status": "error", "error": "draft_not_found", "draft_id": draft_id}

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if data.get("status") != "approved":
            return {"status": "error", "error": "draft_not_approved", "draft_id": draft_id}

        cfg, missing = self._resolve_smtp(smtp_cfg)
        if missing:
            return {
                "status": "send_simulated",
                "mode": "fallback_dry_run",
                "warning": "missing_smtp_env",
                "missing": missing,
                "auth_method": cfg.get("auth_method", "basic"),
                "draft_id": draft_id,
                "to": data.get("to"),
                "subject": data.get("subject"),
            }

        if dry_run:
            return {
                "status": "send_simulated",
                "mode": "dry_run",
                "auth_method": cfg.get("auth_method", "basic"),
                "draft_id": draft_id,
                "to": data.get("to"),
                "subject": data.get("subject"),
            }

        msg = EmailMessage()
        msg["From"] = cfg["from_addr"]
        msg["To"] = data.get("to", "")
        msg["Subject"] = data.get("subject", "")
        msg.set_content(data.get("body", ""))

        with smtplib.SMTP(cfg["host"], cfg["port"], timeout=20) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            self._smtp_auth(server, cfg)
            server.send_message(msg)

        data["status"] = "sent"
        data["sent_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return {
            "status": "sent",
            "auth_method": cfg.get("auth_method", "basic"),
            "draft_id": draft_id,
            "path": path,
        }


def main():
    parser = argparse.ArgumentParser(description="GrayWolf Mail Tool")
    parser.add_argument("--action", choices=["draft", "confirm", "send", "check-smtp", "test-smtp", "validate-provider"], required=True)
    parser.add_argument("--to")
    parser.add_argument("--subject")
    parser.add_argument("--body")
    parser.add_argument("--draft-id")
    parser.add_argument("--approved", choices=["true", "false"], default="false")
    parser.add_argument("--dry-run", choices=["true", "false"], default="true")
    parser.add_argument("--smtp-host")
    parser.add_argument("--smtp-port")
    parser.add_argument("--smtp-user")
    parser.add_argument("--smtp-pass")
    parser.add_argument("--smtp-from")
    parser.add_argument("--smtp-auth-method", choices=["basic", "oauth2"])
    parser.add_argument("--smtp-oauth2-token")
    parser.add_argument("--provider", choices=["gmail", "outlook"])
    args = parser.parse_args()

    tool = MailTool()
    smtp_cfg = {
        "host": args.smtp_host,
        "port": args.smtp_port,
        "user": args.smtp_user,
        "password": args.smtp_pass,
        "from_addr": args.smtp_from,
        "auth_method": args.smtp_auth_method,
        "oauth2_token": args.smtp_oauth2_token,
    }

    if args.action == "check-smtp":
        cfg, missing = tool._resolve_smtp(smtp_cfg)
        if missing:
            print(
                json.dumps(
                    {
                        "status": "warning",
                        "warning": "missing_smtp_env",
                        "missing": missing,
                        "fallback": "dry_run",
                        "auth_method": cfg.get("auth_method", "basic"),
                    },
                    ensure_ascii=False,
                )
            )
        else:
            print(
                json.dumps(
                    {"status": "ok", "smtp_env": "configured", "auth_method": cfg.get("auth_method", "basic")},
                    ensure_ascii=False,
                )
            )
        return

    if args.action == "validate-provider":
        if not args.provider:
            print(json.dumps({"status": "error", "error": "missing_provider"}, ensure_ascii=False))
            return
        print(json.dumps(validate_provider_env(args.provider), ensure_ascii=False))
        return

    if args.action == "test-smtp":
        print(json.dumps(tool.test_smtp(smtp_cfg), ensure_ascii=False))
        return

    if args.action == "draft":
        if not (args.to and args.subject and args.body):
            print(json.dumps({"status": "error", "error": "missing_fields"}, ensure_ascii=False))
            return
        print(json.dumps(tool.create_draft(args.to, args.subject, args.body), ensure_ascii=False))
        return

    if not args.draft_id:
        print(json.dumps({"status": "error", "error": "missing_draft_id"}, ensure_ascii=False))
        return

    if args.action == "confirm":
        approved = args.approved.lower() == "true"
        print(json.dumps(tool.confirm_draft(args.draft_id, approved), ensure_ascii=False))
        return

    dry_run = args.dry_run.lower() == "true"
    print(json.dumps(tool.send_draft(args.draft_id, dry_run=dry_run, smtp_cfg=smtp_cfg), ensure_ascii=False))


if __name__ == "__main__":
    main()
