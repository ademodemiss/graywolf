import os


def _looks_email(value: str) -> bool:
    return "@" in value and "." in value.split("@")[-1]


def validate_provider_env(provider: str, env: dict | None = None) -> dict:
    env = env or os.environ
    p = (provider or "").strip().lower()

    if p == "gmail":
        expected_host = "smtp.gmail.com"
        expected_auth = "basic"
    elif p == "outlook":
        expected_host = "smtp-mail.outlook.com"
        expected_auth = "basic"
    else:
        return {"status": "error", "error": "unsupported_provider", "provider": provider}

    missing = []
    warnings = []
    invalid_format = []

    required = ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_FROM", "SMTP_PASS"]
    for k in required:
        if not (env.get(k) or "").strip():
            missing.append(k)

    host = (env.get("SMTP_HOST") or "").strip().lower()
    if host and host != expected_host:
        warnings.append(f"SMTP_HOST expected={expected_host} actual={host}")

    port = (env.get("SMTP_PORT") or "").strip()
    if port and port != "587":
        warnings.append(f"SMTP_PORT recommended=587 actual={port}")

    auth = (env.get("SMTP_AUTH_METHOD") or "basic").strip().lower()
    if auth != expected_auth:
        warnings.append(f"SMTP_AUTH_METHOD expected={expected_auth} actual={auth}")

    user = (env.get("SMTP_USER") or "").strip()
    from_addr = (env.get("SMTP_FROM") or "").strip()
    if user and not _looks_email(user):
        invalid_format.append("SMTP_USER")
    if from_addr and not _looks_email(from_addr):
        invalid_format.append("SMTP_FROM")

    if p == "gmail" and (env.get("SMTP_PASS") or "").strip() and len((env.get("SMTP_PASS") or "").replace(" ", "")) < 16:
        warnings.append("SMTP_PASS may not be Gmail App Password (expected 16 chars)")

    status = "ok" if not missing and not invalid_format else "warning"
    return {
        "status": status,
        "provider": p,
        "missing": missing,
        "invalid_format": invalid_format,
        "warnings": warnings,
    }
