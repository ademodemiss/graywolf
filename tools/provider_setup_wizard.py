import argparse
import json


def provider_schema(provider: str) -> dict:
    p = provider.lower().strip()
    if p == "gmail":
        return {
            "provider": "gmail",
            "env": {
                "SMTP_HOST": "smtp.gmail.com",
                "SMTP_PORT": "587",
                "SMTP_USER": "<your_gmail_address>",
                "SMTP_PASS": "<app_password_16_chars>",
                "SMTP_FROM": "<your_gmail_address>",
                "SMTP_AUTH_METHOD": "basic",
            },
            "notes": [
                "2FA açık olmalı.",
                "SMTP_PASS için normal şifre değil App Password kullanılmalı.",
            ],
        }

    if p == "outlook":
        return {
            "provider": "outlook",
            "env": {
                "SMTP_HOST": "smtp-mail.outlook.com",
                "SMTP_PORT": "587",
                "SMTP_USER": "<your_outlook_address>",
                "SMTP_PASS": "<app_password_or_provider_password>",
                "SMTP_FROM": "<your_outlook_address>",
                "SMTP_AUTH_METHOD": "basic",
            },
            "notes": [
                "Basic SMTP bazı hesaplarda policy nedeniyle kapalı olabilir (535/5.7.139).",
                "Gerekirse OAuth2/Graph yoluna geçilmelidir.",
            ],
        }

    raise ValueError(f"Unsupported provider: {provider}")


def to_env_lines(schema: dict, mask_secrets: bool = True) -> str:
    secret_keys = {"SMTP_PASS", "SMTP_OAUTH2_TOKEN", "GRAPH_ACCESS_TOKEN"}
    lines = []
    for k, v in schema.get("env", {}).items():
        if mask_secrets and k in secret_keys:
            lines.append(f"{k}=***")
        else:
            lines.append(f"{k}={v}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="GrayWolf provider setup wizard")
    parser.add_argument("--provider", choices=["gmail", "outlook"], required=True)
    parser.add_argument("--format", choices=["json", "env"], default="json")
    parser.add_argument("--show-secrets", action="store_true")
    args = parser.parse_args()

    schema = provider_schema(args.provider)

    if args.format == "env":
        print(to_env_lines(schema, mask_secrets=not args.show_secrets))
        return

    if not args.show_secrets:
        masked = dict(schema)
        masked["env"] = {
            k: ("***" if k in {"SMTP_PASS", "SMTP_OAUTH2_TOKEN", "GRAPH_ACCESS_TOKEN"} else v)
            for k, v in schema.get("env", {}).items()
        }
        print(json.dumps(masked, ensure_ascii=False, indent=2))
        return

    print(json.dumps(schema, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
