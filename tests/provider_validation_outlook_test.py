import json
import os

from tools.provider_validation import validate_provider_env


if __name__ == "__main__":
    env = dict(os.environ)
    env.update(
        {
            "SMTP_HOST": "smtp-mail.outlook.com",
            "SMTP_PORT": "587",
            "SMTP_USER": "demo@outlook.com",
            "SMTP_FROM": "demo@outlook.com",
            "SMTP_PASS": "example-pass",
            "SMTP_AUTH_METHOD": "basic",
        }
    )
    print(json.dumps(validate_provider_env("outlook", env), ensure_ascii=False))
