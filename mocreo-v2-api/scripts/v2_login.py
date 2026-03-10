import os
import argparse
import requests
import json
import sys
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.sync-sign.com/v2"

def main():
    parser = argparse.ArgumentParser(description="MOCREO v2 API: Get oauth token")
    parser.add_argument("--username", default=os.getenv("MOCREO_V2_USER"), help="Username (can be set via MOCREO_V2_USER env var)")
    parser.add_argument("--password", default=os.getenv("MOCREO_V2_PASS"), help="Password (can be set via MOCREO_V2_PASS env var)")
    args = parser.parse_args()

    if not args.username or not args.password:
        print("Error: Username and password are required. Provide them via arguments or .env file.")
        sys.exit(1)

    url = f"{BASE_URL}/oauth/token"
    payload = {
        "grant_type": "password",
        "username": args.username,
        "password": args.password,
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