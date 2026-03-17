import requests
import argparse
import sys

def update_device_name(auth_val, asset_id, device_id, name, is_apikey=False):
    url = f"https://api.mocreo.com/v1/assets/{asset_id}/devices/{device_id}/name"
    headers = {"X-API-Key": auth_val} if is_apikey else {"Authorization": f"Bearer {auth_val}"}
    headers["Content-Type"] = "application/json"
    payload = {"name": name}
    try:
        r = requests.patch(url, json=payload, headers=headers)
        if r.status_code == 200:
            print(r.text)
        else:
            print(f"ERROR: {r.status_code} - {r.text}", file=sys.stderr)
            sys.exit(1)
    except Exception as e: print(e, file=sys.stderr); sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--auth", required=True)
    parser.add_argument("--asset_id", required=True)
    parser.add_argument("--device_id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--apikey", action="store_true")
    args = parser.parse_args()
    update_device_name(args.auth, args.asset_id, args.device_id, args.name, args.apikey)
