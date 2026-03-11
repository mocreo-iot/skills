import argparse
import requests
import json
import sys

BASE_URL = "https://api.sync-sign.com/v2"

def main():
    parser = argparse.ArgumentParser(description="MOCREO v2 API: Get specific device details")
    parser.add_argument("--token", required=True, help="Bearer token")
    parser.add_argument("--sn", required=True, help="Device serial number")
    args = parser.parse_args()

    url = f"{BASE_URL}/devices/{args.sn}"
    headers = {"Authorization": f"Bearer {args.token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if e.response is not None:
            print(e.response.text)
        sys.exit(1)

if __name__ == "__main__":
    main()