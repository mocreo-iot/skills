import argparse
import sys
from pathlib import Path

import requests

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from common.mocreo_auth import (
    ENV_PATH,
    delete_env_keys,
    resolve_credentials,
    write_env_values,
)


def snapshot_shared_credentials():
    keys = ("MOCREO_USER", "MOCREO_PASS", "MOCREO_PLATFORM")
    snapshot = {}
    if not ENV_PATH.exists():
        return snapshot

    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        if key in keys:
            snapshot[key] = value
    return snapshot


def validate_credentials(platform, user, password):
    if platform == "smart":
        response = requests.post(
            "https://api.mocreo.com/v1/users/login",
            json={"email": user, "password": password},
            headers={"Content-Type": "application/json", "Origin": "https://api.mocreo.com"},
            timeout=20,
        )
    elif platform == "sensor":
        response = requests.post(
            "https://api.sync-sign.com/v2/oauth/token",
            json={"username": user, "password": password, "provider": "mocreo"},
            timeout=20,
        )
    else:
        return False, f"Unsupported platform: {platform}"

    if response.ok:
        return True, None

    detail = response.text.strip() or f"HTTP {response.status_code}"
    return False, detail


def restore_previous_credentials(snapshot):
    delete_env_keys("MOCREO_USER", "MOCREO_PASS", "MOCREO_PLATFORM")
    if snapshot:
        write_env_values(snapshot)


def main():
    parser = argparse.ArgumentParser(description="Bootstrap shared MOCREO credentials")
    parser.add_argument("--platform", choices=["smart", "sensor"], default=None)
    args = parser.parse_args()

    previous_snapshot = snapshot_shared_credentials()
    creds = resolve_credentials(
        platform=args.platform,
        allow_prompt=True,
        persist_platform=True,
    )

    try:
        is_valid, error_detail = validate_credentials(
            creds["platform"],
            creds["user"],
            creds["password"],
        )
    except requests.RequestException as exc:
        print(
            "Credentials were saved, but the login check could not complete due to a network error.",
            file=sys.stderr,
        )
        print(f"Validation error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not is_valid:
        restore_previous_credentials(previous_snapshot)
        print(
            "Credential check failed. The entered account, password, or selected platform is not valid.",
            file=sys.stderr,
        )
        print(f"Platform checked: {creds['platform']}", file=sys.stderr)
        print(f"Login response: {error_detail}", file=sys.stderr)
        print(
            "Your previous shared credentials were restored. Please rerun the setup and try again.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Saved credentials to {creds['env_path']}")
    print(f"Default platform: {creds['platform']}")
    print("Credential check passed.")
    print("Password was captured in the terminal with hidden input and stored only in the local .env file.")


if __name__ == "__main__":
    main()
