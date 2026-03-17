import argparse
import requests
import json
import sys

BASE_URL = "https://api.sync-sign.com/v2"

def main():
    parser = argparse.ArgumentParser(description="MOCREO v2 API: Get alerts")
    parser.add_argument("--token", required=True, help="Bearer token")
    parser.add_argument("--limit", type=int, default=10, help="Limit number of alerts")
    parser.add_argument("--offset", type=int, help="Number of rows to skip before returning data")
    parser.add_argument("--dismissed", choices=["true", "false"], help="Filter alerts by dismissed state")
    parser.add_argument("--begin_time", help="Begin time in seconds")
    parser.add_argument("--end_time", help="End time in seconds")
    parser.add_argument("--start", dest="start_legacy", help="Backward-compatible alias for --begin_time")
    parser.add_argument("--end", dest="end_legacy", help="Backward-compatible alias for --end_time")
    parser.add_argument("--node_id", help="Deprecated. The live Swagger does not document node filtering on /alerts.")
    args = parser.parse_args()

    if args.start_legacy and not args.begin_time:
        args.begin_time = args.start_legacy
    if args.end_legacy and not args.end_time:
        args.end_time = args.end_legacy

    url = f"{BASE_URL}/alerts"
    headers = {"Authorization": f"Bearer {args.token}"}
    params = {"limit": args.limit}
    if args.offset is not None:
        params["offset"] = args.offset
    if args.dismissed is not None:
        params["dismissed"] = args.dismissed
    if args.begin_time:
        params["beginTime"] = args.begin_time
    if args.end_time:
        params["endTime"] = args.end_time

    if args.node_id:
        print(
            "Warning: --node_id is not documented by the live Swagger for /alerts and will be ignored.",
            file=sys.stderr,
        )
    
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
