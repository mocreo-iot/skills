import requests
import argparse
import sys

def get_asset(auth_val, asset_id, is_apikey=False):
    url = f"https://api.mocreo.com/v1/assets/{asset_id}"
    headers = {"X-API-Key": auth_val} if is_apikey else {"Authorization": f"Bearer {auth_val}"}
    try:
        r = requests.get(url, headers=headers)
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
    parser.add_argument("--apikey", action="store_true")
    args = parser.parse_args()
    get_asset(args.auth, args.asset_id, args.apikey)
