import argparse
import requests
import json
import sys

BASE_URL = "https://api.sync-sign.com/v2"

def main():
    parser = argparse.ArgumentParser(description="MOCREO v2 API: Refresh oauth token")
    parser.add_argument("--refresh_token", required=True, help="Refresh Token")
    args = parser.parse_args()

    url = f"{BASE_URL}/oauth/token/refresh"
    payload = {
        "grant_type": "refresh_token",
        "refreshToken": args.refresh_token,
        "provider": "mocreo"
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if e.response is not None:
            print(e.response.text)
        sys.exit(1)

if __name__ == "__main__":
    main()