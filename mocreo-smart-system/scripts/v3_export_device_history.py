import requests
import argparse
import sys

def export_history(auth_val, asset_id, device_id, email, start, end, tz, fields, is_apikey=False):
    url = f"https://api.mocreo.com/v1/assets/{asset_id}/devices/{device_id}/history/export"
    
    # Dynamically select authentication method
    if is_apikey:
        headers = {"X-API-Key": auth_val}
    else:
        headers = {"Authorization": f"Bearer {auth_val}"}
        
    params = {"email": email, "from": start, "to": end, "tz": tz, "fields": fields}
    
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
    parser.add_argument("--auth", required=True, help="Token or API Key")
    parser.add_argument("--asset_id", required=True)
    parser.add_argument("--device_id", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--tz", required=True)
    parser.add_argument("--fields", required=True)
    parser.add_argument("--apikey", action="store_true", help="Use X-API-Key instead of Bearer")
    args = parser.parse_args()
    export_history(args.auth, args.asset_id, args.device_id, args.email, args.start, args.end, args.tz, args.fields, args.apikey)
