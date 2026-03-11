import requests
import argparse
import sys

def get_history(auth_val, asset_id, device_id, start, end, tz, field, window=None, agg=None, limit=None, is_apikey=False):
    url = f"https://api.mocreo.com/v1/assets/{asset_id}/devices/{device_id}/history"
    headers = {"X-API-Key": auth_val} if is_apikey else {"Authorization": f"Bearer {auth_val}"}
    params = {"from": start, "to": end, "tz": tz, "field": field}
    if window: params["windowDuration"] = window
    if agg: params["aggregationsType"] = agg
    if limit: params["limit"] = limit
    
    try:
        r = requests.get(url, headers=headers, params=params)
        if r.status_code == 200:
            print(r.text)
        else:
            print(f"ERROR: {r.status_code} - {r.text}", file=sys.stderr)
            sys.exit(1)
    except Exception as e: print(e, file=sys.stderr); sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--auth", required=True)
    parser.add_argument("--asset_id", required=True)
    parser.add_argument("--device_id", required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--tz", required=True)
    parser.add_argument("--field", required=True)
    parser.add_argument("--window")
    parser.add_argument("--agg")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--apikey", action="store_true")
    args = parser.parse_args()
    get_history(args.auth, args.asset_id, args.device_id, args.start, args.end, args.tz, args.field, args.window, args.agg, args.limit, args.apikey)
