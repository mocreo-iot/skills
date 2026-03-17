import requests
import argparse
import json
import sys
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from common.mocreo_auth import add_shared_auth_args, build_credentials_from_args

def login(email, password):
    if not email or not password:
        print("ERROR: Email and password are required. Provide them via arguments or .env file.", file=sys.stderr)
        sys.exit(1)

    url = "https://api.mocreo.com/v1/users/login"
    headers = {"Content-Type": "application/json", "Origin": "https://api.mocreo.com"}
    payload = {"email": email, "password": password}
    try:
        r = requests.post(url, json=payload, headers=headers)
        if r.status_code == 200:
            result = r.json().get("result", {})
            # Output full result so callers can extract both access_token and refresh_token
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return
        print(f"ERROR: {r.status_code} - {r.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"EXCEPTION: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    add_shared_auth_args(parser, "Platform for shared credential bootstrap")
    parser.add_argument("--email", default=None, help="Backward-compatible alias for --user")
    args = parser.parse_args()

    if args.email and not args.user:
        args.user = args.email

    if not args.user or not args.password:
        print("MOCREO_CREDENTIALS_MISSING: No credentials found in .env. Run the setup script to configure.", file=sys.stderr)
        sys.exit(2)

    creds = build_credentials_from_args(args, fallback_platform="smart")
    login(creds["user"], creds["password"])
