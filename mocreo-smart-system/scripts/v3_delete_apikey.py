import requests
import argparse
import sys

def delete_apikey(token, asset_id, prefix):
    url = f"https://api.mocreo.com/v1/assets/{asset_id}/apikeys/{prefix}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.delete(url, headers=headers)
        if r.status_code in (200, 204):
            print(r.text)
        else:
            print(f"ERROR: {r.status_code} - {r.text}", file=sys.stderr)
            sys.exit(1)
    except Exception as e: print(e, file=sys.stderr); sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True)
    parser.add_argument("--asset_id", required=True)
    parser.add_argument("--prefix", required=True)
    args = parser.parse_args()
    delete_apikey(args.token, args.asset_id, args.prefix)
