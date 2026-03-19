import argparse
import requests
import json
import sys

BASE_URL = "https://api.sync-sign.com/v2"

def main():
    parser = argparse.ArgumentParser(description="MOCREO v2 API: Update specific node details")
    parser.add_argument("--token", required=True, help="Bearer token")
    parser.add_argument("--node_id", required=True, help="Node ID")
    parser.add_argument("--payload", required=True, help="JSON payload string to update")
    args = parser.parse_args()

    url = f"{BASE_URL}/nodes/{args.node_id}"
    headers = {"Authorization": f"Bearer {args.token}", "Content-Type": "application/json"}
    
    try:
        data = json.loads(args.payload)
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()