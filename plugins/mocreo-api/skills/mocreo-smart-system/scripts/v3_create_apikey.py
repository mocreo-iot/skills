import requests
import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from common.mocreo_auth import (
    extract_apikey_prefix,
    save_v3_apikey_record,
)

VALID_PERMISSIONS = {
    "asset.read",
    "asset.update",
    "device.read",
    "device.update",
    "membership.read",
    "membership.update",
    "membership.delete",
}


def create_apikey(token, asset_id, display_name, permissions, expires_at=None, asset_name=None):
    requested_permissions = [permission.strip() for permission in permissions.split(",") if permission.strip()]
    invalid_permissions = [permission for permission in requested_permissions if permission not in VALID_PERMISSIONS]
    if invalid_permissions:
        print(
            "ERROR: Invalid permissions: "
            f"{', '.join(invalid_permissions)}. Valid values: {', '.join(sorted(VALID_PERMISSIONS))}",
            file=sys.stderr,
        )
        sys.exit(1)

    url = f"https://api.mocreo.com/v1/assets/{asset_id}/apikeys"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"displayName": display_name, "permissions": requested_permissions}
    if expires_at:
        payload["expiresAt"] = expires_at
    try:
        r = requests.post(url, json=payload, headers=headers)
        if r.status_code in (200, 201):
            response_json = r.json()
            result = response_json.get("result", {})
            api_key = result.get("key")
            created_prefix = result.get("prefix") or extract_apikey_prefix(api_key) or "unknown"
            if api_key:
                save_v3_apikey_record(
                    asset_id=asset_id,
                    asset_name=asset_name,
                    api_key=api_key,
                    permissions=requested_permissions,
                    prefix=created_prefix,
                    display_name=result.get("displayName") or display_name,
                    created_at=result.get("createdAt"),
                    expires_at=result.get("expiresAt"),
                )
                response_json.setdefault("messages", []).append("Saved in the local asset-scoped API key registry")
            print(json.dumps(response_json, ensure_ascii=False))
        else:
            print(f"ERROR: {r.status_code} - {r.text}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"EXCEPTION: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True)
    parser.add_argument("--asset_id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--permissions", required=True, help="Comma-separated permissions e.g. device.read,device.update")
    parser.add_argument("--expires_at", help="Optional ISO 8601 expiration time, e.g. 2026-12-31T23:59:59.000Z")
    parser.add_argument("--asset_name", default=None, help="Optional asset display name for local API key registry metadata")
    args = parser.parse_args()
    create_apikey(args.token, args.asset_id, args.name, args.permissions, args.expires_at, args.asset_name)
