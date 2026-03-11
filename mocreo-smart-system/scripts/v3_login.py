import requests
import argparse
import json
import sys
import os
from dotenv import load_dotenv

load_dotenv()

def login(email, password):
    if not email or not password:
        print("ERROR: Email and password are required. Provide them via arguments or .env file.", file=sys.stderr)
        sys.exit(1)

    url = "https://api.mocreo.com/v1/users/login"
    headers = {"Content-Type": "application/json", "Origin": "https://api.mocreo.com"}
    payload = {"email": email, "password": password}
    try:
        r = requests.post(url, json=payload, headers=headers)
        if r.status_code == 200:
            result = r.json().get("result", {})
            # Output full result so callers can extract both access_token and refresh_token
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return
        print(f"ERROR: {r.status_code} - {r.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"EXCEPTION: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", default=os.getenv("MOCREO_V3_EMAIL"))
    parser.add_argument("--password", default=os.getenv("MOCREO_V3_PASS"))
    args = parser.parse_args()
    login(args.email, args.password)
