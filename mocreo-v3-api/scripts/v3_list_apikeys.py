import requests
import argparse
import sys

def list_apikeys(token, asset_id):
    url = f"https://api.mocreo.com/v1/assets/{asset_id}/apikeys"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(url, headers=headers)
        print(r.text)
        if r.status_code != 200: sys.exit(1)
    except Exception as e: print(e, file=sys.stderr); sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True)
    parser.add_argument("--asset_id", required=True)
    args = parser.parse_args()
    list_apikeys(args.token, args.asset_id)
