import requests
import argparse
import sys

def refresh_token(token, refresh_token):
    url = f"https://api.mocreo.com/v1/users/refreshToken?refreshToken={refresh_token}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            print(r.text)
            return
        print(f"ERROR: {r.status_code} - {r.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"EXCEPTION: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True)
    parser.add_argument("--refresh_token", required=True)
    args = parser.parse_args()
    refresh_token(args.token, args.refresh_token)
