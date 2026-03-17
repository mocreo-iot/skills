import argparse
import requests
import json
import sys

BASE_URL = "https://api.sync-sign.com/v2"

def main():
    parser = argparse.ArgumentParser(description="MOCREO v2 API: Dismiss all alerts")
    parser.add_argument("--token", required=True, help="Bearer token")
    args = parser.parse_args()

    url = f"{BASE_URL}/alerts/dismiss_all"
    headers = {"Authorization": f"Bearer {args.token}"}
    
    try:
        response = requests.put(url, headers=headers)
        response.raise_for_status()
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if e.response is not None:
            print(e.response.text)
        sys.exit(1)

if __name__ == "__main__":
    main()