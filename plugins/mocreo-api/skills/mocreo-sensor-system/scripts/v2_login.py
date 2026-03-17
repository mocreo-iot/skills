import os
import argparse
import requests
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from common.mocreo_auth import add_shared_auth_args, build_credentials_from_args

BASE_URL = "https://api.sync-sign.com/v2"

def main():
    parser = argparse.ArgumentParser(description="MOCREO v2 API: Get oauth token")
    add_shared_auth_args(parser, "Platform for shared credential bootstrap")
    parser.add_argument("--username", default=None, help="Backward-compatible alias for --user")
    parser.add_argument("--password-legacy", dest="password_legacy", default=None, help="Backward-compatible alias for --password")
    args = parser.parse_args()

    if args.username and not args.user:
        args.user = args.username
    if args.password_legacy and not args.password:
        args.password = args.password_legacy

    if not args.user or not args.password:
        print("MOCREO_CREDENTIALS_MISSING: No credentials found in .env. Run the setup script to configure.", file=sys.stderr)
        sys.exit(2)

    creds = build_credentials_from_args(args, fallback_platform="sensor")

    if not creds["user"] or not creds["password"]:
        print("Error: Username and password are required. Provide them via arguments or the bootstrap prompt.")
        sys.exit(1)

    url = f"{BASE_URL}/oauth/token"
    payload = {
        "username": creds["user"],
        "password": creds["password"],
        "provider": "mocreo"
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if e.response is not None:
            print(e.response.text)
        sys.exit(1)

if __name__ == "__main__":
    main()
