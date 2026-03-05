import json
import os

from tools.provider_validation import validate_provider_env


if __name__ == "__main__":
    env = dict(os.environ)
    env.update(
        {
            "SMTP_HOST": "smtp.gmail.com",
            "SMTP_PORT": "587",
            "SMTP_USER": "demo@gmail.com",
            "SMTP_FROM": "demo@gmail.com",
            "SMTP_PASS": "abcd efgh ijkl mnop",
            "SMTP_AUTH_METHOD": "basic",
        }
    )
    print(json.dumps(validate_provider_env("gmail", env), ensure_ascii=False))
