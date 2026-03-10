import requests
import argparse
import sys

def get_device(auth_val, asset_id, device_id, is_apikey=False):
    url = f"https://api.mocreo.com/v1/assets/{asset_id}/devices/{device_id}"
    headers = {"X-API-Key": auth_val} if is_apikey else {"Authorization": f"Bearer {auth_val}"}
    try:
        r = requests.get(url, headers=headers)
        print(r.text)
        if r.status_code != 200: sys.exit(1)
    except Exception as e: print(e, file=sys.stderr); sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--auth", required=True)
    parser.add_argument("--asset_id", required=True)
    parser.add_argument("--device_id", required=True)
    parser.add_argument("--apikey", action="store_true")
    args = parser.parse_args()
    get_device(args.auth, args.asset_id, args.device_id, args.apikey)
