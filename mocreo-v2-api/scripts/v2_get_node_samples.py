import argparse
import requests
import json
import sys

BASE_URL = "https://api.sync-sign.com/v2"

def main():
    parser = argparse.ArgumentParser(description="MOCREO v2 API: Get node samples (history)")
    parser.add_argument("--token", required=True, help="Bearer token")
    parser.add_argument("--node_id", required=True, help="Node ID")
    parser.add_argument("--start", help="Start timestamp")
    parser.add_argument("--end", help="End timestamp")
    parser.add_argument("--limit", type=int, default=1, help="Limit number of samples")
    args = parser.parse_args()

    url = f"{BASE_URL}/nodes/{args.node_id}/samples"
    headers = {"Authorization": f"Bearer {args.token}"}
    params = {"limit": args.limit}
    if args.start:
        params['start'] = args.start
    if args.end:
        params['end'] = args.end
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if e.response is not None:
            print(e.response.text)
        sys.exit(1)

if __name__ == "__main__":
    main()