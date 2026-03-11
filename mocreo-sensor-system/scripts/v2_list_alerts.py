import argparse
import requests
import json
import sys

BASE_URL = "https://api.sync-sign.com/v2"

def main():
    parser = argparse.ArgumentParser(description="MOCREO v2 API: Get alerts")
    parser.add_argument("--token", required=True, help="Bearer token")
    parser.add_argument("--node_id", help="Filter alerts by Node ID")
    parser.add_argument("--limit", type=int, default=10, help="Limit number of alerts")
    parser.add_argument("--start", help="Start timestamp (milliseconds)")
    parser.add_argument("--end", help="End timestamp (milliseconds)")
    args = parser.parse_args()

    url = f"{BASE_URL}/alerts"
    headers = {"Authorization": f"Bearer {args.token}"}
    params = {"limit": args.limit}
    if args.node_id:
        params['nodeId'] = args.node_id
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