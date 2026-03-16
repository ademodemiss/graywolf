from __future__ import annotations

import argparse
import json
from collections import OrderedDict
from pathlib import Path
from typing import Iterable

try:
    from tools.provider_validation import (
        PROVIDER_PROFILES,
        SECRET_STORAGE_GUIDANCE,
        validate_provider_env,
    )
except ModuleNotFoundError:
    from provider_validation import (
        PROVIDER_PROFILES,
        SECRET_STORAGE_GUIDANCE,
        validate_provider_env,
    )

SECRET_FIELDS = {"SMTP_PASS", "SMTP_OAUTH2_TOKEN", "GRAPH_ACCESS_TOKEN"}


def _load_env_file(path: str) -> tuple[dict[str, str], str | None]:
    if not path:
        return {}, None
    env_path = Path(path).expanduser()
    if not env_path.exists():
        return {}, f"{path} not found"

    result: dict[str, str] = {}
    with env_path.open(encoding="utf-8") as handle:
        for line in handle:
            cleaned = line.strip()
            if not cleaned or cleaned.startswith("#"):
                continue
            if "=" not in cleaned:
                continue
            key, value = cleaned.split("=", 1)
            result[key.strip()] = value.strip()
    return result, None


def _mask_value(key: str, value: str, reveal: bool) -> str:
    if reveal or key not in SECRET_FIELDS:
        return value
    if value:
        return "***"
    return value


def _build_template(provider: str) -> OrderedDict[str, str]:
    profile = PROVIDER_PROFILES[provider]
    template = OrderedDict(
        [
            ("SMTP_PROVIDER", provider),
            ("SMTP_HOST", profile["host"]),
            ("SMTP_PORT", str(profile["port"])),
            ("SMTP_AUTH_METHOD", profile["auth_method"]),
            ("SMTP_USER", "<you@example.com>"),
            ("SMTP_FROM", "<you@example.com>"),
            (profile["secret_key"], profile["secret_placeholder"]),
        ]
    )
    return template


def _format_env_block(template: OrderedDict[str, str], reveal_secrets: bool) -> str:
    lines = []
    for key, value in template.items():
        lines.append(f"{key}={_mask_value(key, value, reveal_secrets)}")
    return "\n".join(lines)


def _validation_lines(validation: dict, source_desc: str, env_note: str | None) -> list[str]:
    lines = [f"# Validation (source: {source_desc})", f"#   status: {validation.get('status')}"]
    if env_note:
        lines.append(f"#   note: {env_note}")
    if validation.get("issues"):
        lines.append("#   issues:")
        for issue in validation["issues"]:
            lines.append(
                f"#     - {issue['type']} / {issue['field']}: {issue['message']}"
            )
    else:
        lines.append("#   issues: none detected")
    return lines


def _print_env_output(
    provider: str,
    block: str,
    validation: dict,
    source: str,
    env_note: str | None,
    profile_notes: Iterable[str],
    secure_tips: Iterable[str],
) -> None:
    print(f"# GrayWolf Provider Setup — {PROVIDER_PROFILES[provider]['label']} \n# Copy the block below into your .env and replace secrets with actual values.")
    print(block)
    print("#")
    print("# Notes:")
    for note in profile_notes:
        print(f"#   - {note}")
    print("#")
    print("# Secure storage guidance:")
    for tip in secure_tips:
        print(f"#   - {tip}")
    print("#")
    for line in _validation_lines(validation, source, env_note):
        print(line)


def _json_payload(
    provider: str,
    template: OrderedDict[str, str],
    validation: dict,
    source: str,
    env_note: str | None,
    profile_notes: Iterable[str],
    secure_tips: Iterable[str],
    reveal_secrets: bool,
) -> dict:
    masked_template = OrderedDict(
        (key, _mask_value(key, value, reveal_secrets)) for key, value in template.items()
    )
    return {
        "provider": provider,
        "profile": PROVIDER_PROFILES[provider]["label"],
        "template": masked_template,
        "notes": list(profile_notes),
        "secure_storage": list(secure_tips),
        "validation_source": source,
        "validation_note": env_note,
        "validation": validation,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="GrayWolf provider setup wizard")
    parser.add_argument("--provider", choices=list(PROVIDER_PROFILES), required=True)
    parser.add_argument("--format", choices=["env", "json"], default="env")
    parser.add_argument("--env-file", help="Optional .env file to validate (defaults to system env)")
    parser.add_argument(
        "--reveal-secrets",
        action="store_true",
        help="Show secret placeholders directly instead of masking",
    )
    args = parser.parse_args()

    provider = args.provider
    template = _build_template(provider)
    env_data, env_note = _load_env_file(args.env_file) if args.env_file else ({}, None)
    if args.env_file and env_note:
        validation_source = "system environment"
        env_for_validation = None
    else:
        validation_source = args.env_file if args.env_file else "system environment"
        env_for_validation = env_data if env_data else None

    validation = validate_provider_env(provider, env=env_for_validation)
    secure_tips = list(SECRET_STORAGE_GUIDANCE) + PROVIDER_PROFILES[provider].get(
        "secure_storage", []
    )
    if args.format == "env":
        block = _format_env_block(template, args.reveal_secrets)
        _print_env_output(
            provider,
            block,
            validation,
            validation_source,
            env_note,
            PROVIDER_PROFILES[provider].get("notes", []),
            secure_tips,
        )
        return

    payload = _json_payload(
        provider,
        template,
        validation,
        validation_source,
        env_note,
        PROVIDER_PROFILES[provider].get("notes", []),
        secure_tips,
        args.reveal_secrets,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
