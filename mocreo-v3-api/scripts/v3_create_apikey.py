import requests
import argparse
import json
import sys

def create_apikey(token, asset_id, display_name, permissions):
    url = f"https://api.mocreo.com/v1/assets/{asset_id}/apikeys"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"displayName": display_name, "permissions": permissions.split(',')}
    try:
        r = requests.post(url, json=payload, headers=headers)
        print(r.text)
        if r.status_code != 200: sys.exit(1)
    except Exception as e:
        print(f"EXCEPTION: {e}", file=sys.stderr); sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True)
    parser.add_argument("--asset_id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--permissions", required=True, help="Comma-separated permissions e.g. device.read,device.update")
    args = parser.parse_args()
    create_apikey(args.token, args.asset_id, args.name, args.permissions)
