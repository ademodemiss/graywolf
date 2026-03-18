from __future__ import annotations

import os
from typing import Mapping

PROVIDER_PROFILES = {
    "gmail": {
        "label": "Gmail",
        "host": "smtp.gmail.com",
        "port": 587,
        "auth_method": "basic",
        "secret_key": "SMTP_PASS",
        "secret_placeholder": "<app_password_16_chars>",
        "notes": [
            "2FA açık olmalı ve Google hesabında uygulama şifresi üretilmiş olmalı (16 karakter).",
            "SMTP bağlantı hatalarında Google hesabındaki güvenlik uyarılarını kontrol et.",
        ],
        "secure_storage": [
            "App password dâhil tüm secret değerleri Git veya chat loglarına yazmayın.",
            "Yeni bir app password oluşturduğunuzda eski şifreyi iptal edin (rotate).",
        ],
    },
    "outlook": {
        "label": "Outlook",
        "host": "smtp-mail.outlook.com",
        "port": 587,
        "auth_method": "basic",
        "secret_key": "SMTP_PASS",
        "secret_placeholder": "<app_password_or_account_password>",
        "notes": [
            "Temel SMTP bazen Outlook policy nedeniyle kapalıdır; oauth2 veya Graph path düşünülebilir.",
            "Temel auth çalışmazsa Outlook hesap ayarlarından uygulama şifresi üret veya 2FA aç."
        ],
        "secure_storage": [
            "SMTP_PASS değerini güvenli vault/OS keyring içinde saklayın, .env dosyasını repository dışına taşıyın.",
            "Güvenlik ihlali şüphesi varsa secrets rotasyonu yapın ve eski değerleri iptal edin.",
        ],
    },
}

SECRET_STORAGE_GUIDANCE = [
    "Secret değerlerini düz metin olarak Git, Slack veya Telegram gibi ortamlarda paylaşmayın.",
    "Her rotasyon sonrası eski secret'ı iptal edin ve yeni secret'ı sadece güvenli ortamda saklayın.",
    "`.env` dosyanız repository'e commit edilmemeli; deployment için ortam değişkeni enjeksiyonu tercih edin.",
]

SECRET_FIELDS = {"SMTP_PASS", "SMTP_OAUTH2_TOKEN", "GRAPH_ACCESS_TOKEN"}


def _looks_email(value: str) -> bool:
    return "@" in value and "." in value.split("@")[-1]


def _normalize_env(env: Mapping[str, str] | None) -> dict[str, str]:
    source = env if env is not None else os.environ
    normalized: dict[str, str] = {}
    for key, value in source.items():
        normalized_key = str(key).strip()
        normalized_value = "" if value is None else str(value).strip()
        normalized[normalized_key] = normalized_value
    return normalized


def _mask_value(field: str, value: str) -> str:
    if field in SECRET_FIELDS and value:
        return "***"
    return value


def validate_provider_env(provider: str, env: Mapping[str, str] | None = None) -> dict:
    normalized = _normalize_env(env)
    p = (provider or "").strip().lower()

    profile = PROVIDER_PROFILES.get(p)
    if not profile:
        return {"status": "error", "error": "unsupported_provider", "provider": provider}

    auth_method = normalized.get("SMTP_AUTH_METHOD", profile["auth_method"]).strip().lower()
    base_fields = ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_FROM"]
    secret_field = "SMTP_OAUTH2_TOKEN" if auth_method == "oauth2" else profile["secret_key"]
    required_fields = base_fields + [secret_field]

    issues: list[dict[str, str]] = []
    missing: list[str] = []
    invalid_format: list[str] = []
    warnings: list[str] = []

    def add_issue(issue_type: str, field: str, message: str) -> None:
        issues.append({"type": issue_type, "field": field, "message": message})
        if issue_type == "missing" and field not in missing:
            missing.append(field)
        if issue_type == "invalid_format" and field not in invalid_format:
            invalid_format.append(field)
        if issue_type == "warning" and message not in warnings:
            warnings.append(message)

    for field in required_fields:
        value = normalized.get(field, "")
        if not value:
            add_issue("missing", field, f"{field} is required for {profile['label']}.")

    host = normalized.get("SMTP_HOST", "")
    if host and host.lower() != profile["host"]:
        add_issue("warning", "SMTP_HOST", f"recommended {profile['host']} but got {host}")

    port = normalized.get("SMTP_PORT", "")
    if port and port != str(profile["port"]):
        add_issue("warning", "SMTP_PORT", f"recommended {profile['port']} but got {port}")

    if auth_method != profile["auth_method"]:
        add_issue(
            "warning",
            "SMTP_AUTH_METHOD",
            f"expected {profile['auth_method']} but got {auth_method}",
        )

    for email_field in ("SMTP_USER", "SMTP_FROM"):
        candidate = normalized.get(email_field, "")
        if candidate and not _looks_email(candidate):
            add_issue("invalid_format", email_field, f"{email_field} should look like an email address.")

    secret_value = normalized.get(secret_field, "")
    if p == "gmail" and secret_value:
        compact_secret = secret_value.replace(" ", "")
        if len(compact_secret) < 16:
            add_issue("warning", secret_field, "Gmail app password is 16 characters long.")

    if p == "outlook" and secret_value:
        compact_secret = secret_value.replace(" ", "")
        if len(compact_secret) < 8:
            add_issue(
                "warning",
                secret_field,
                "Outlook şifreleri yeterince uzun değil; rotate ve güçlü parola kullanın.",
            )

    if issues:
        status = "error" if missing else "warning"
    else:
        status = "ok"

    value_snapshot = {
        field: _mask_value(field, normalized.get(field, "")) for field in required_fields
    }

    return {
        "status": status,
        "provider": p,
        "profile": profile["label"],
        "issues": issues,
        "missing": missing,
        "invalid_format": invalid_format,
        "warnings": warnings,
        "counts": {"missing": len(missing), "invalid_format": len(invalid_format), "warnings": len(warnings)},
        "expected": {
            "host": profile["host"],
            "port": profile["port"],
            "auth_method": profile["auth_method"],
        },
        "value_snapshot": value_snapshot,
        "notes": profile.get("notes", []),
        "secure_storage": profile.get("secure_storage", []),
    }


__all__ = [
    "PROVIDER_PROFILES",
    "SECRET_STORAGE_GUIDANCE",
    "validate_provider_env",
]
