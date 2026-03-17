import requests
import argparse
import json
import sys

def list_assets(token):
    url = "https://api.mocreo.com/v1/assets"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            assets = r.json().get("result", [])
            print(json.dumps(assets, indent=2, ensure_ascii=False))
            return
        print(f"ERROR: {r.status_code} - {r.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"EXCEPTION: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True)
    args = parser.parse_args()
    list_assets(args.token)
