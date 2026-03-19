import requests
import argparse
import sys

VALID_FIELDS = {"temperature", "humidity", "water_leak", "water_level", "frozen"}


def export_history(auth_val, asset_id, device_id, email, start, end, tz, fields, window=None, agg=None, is_apikey=False):
    requested_fields = [field.strip() for field in fields.split(",") if field.strip()]
    invalid_fields = [field for field in requested_fields if field not in VALID_FIELDS]
    if invalid_fields:
        print(
            f"ERROR: Invalid fields: {', '.join(invalid_fields)}. Valid values: {', '.join(sorted(VALID_FIELDS))}",
            file=sys.stderr,
        )
        sys.exit(1)
    if agg and not window:
        print("ERROR: --agg requires --window.", file=sys.stderr)
        sys.exit(1)

    url = f"https://api.mocreo.com/v1/assets/{asset_id}/devices/{device_id}/history/export"
    
    # Dynamically select authentication method
    if is_apikey:
        headers = {"X-API-Key": auth_val}
    else:
        headers = {"Authorization": f"Bearer {auth_val}"}
        
    params = {"email": email, "from": start, "to": end, "tz": tz, "fields": fields}
    if window:
        params["windowDuration"] = window
    if agg:
        params["aggregationsType"] = agg
    
    try:
        r = requests.get(url, headers=headers, params=params)
        if r.status_code == 200:
            print(r.text)
        else:
            print(f"ERROR: {r.status_code} - {r.text}", file=sys.stderr)
            sys.exit(1)
    except Exception as e: print(e, file=sys.stderr); sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Export device history for a time range. This API is time-range-based and does not support exporting an exact row count."
    )
    parser.add_argument("--auth", required=True, help="Token or API Key")
    parser.add_argument("--asset_id", required=True)
    parser.add_argument("--device_id", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--start", required=True, help="Inclusive or API-defined lower time boundary in milliseconds")
    parser.add_argument("--end", required=True, help="Inclusive or API-defined upper time boundary in milliseconds")
    parser.add_argument("--tz", required=True)
    parser.add_argument("--fields", required=True, help="Comma-separated history fields to export")
    parser.add_argument("--window", "--window_duration", dest="window")
    parser.add_argument("--agg", "--aggregations_type", dest="agg")
    parser.add_argument("--apikey", action="store_true", help="Use X-API-Key instead of Bearer")
    args = parser.parse_args()
    export_history(
        args.auth,
        args.asset_id,
        args.device_id,
        args.email,
        args.start,
        args.end,
        args.tz,
        args.fields,
        args.window,
        args.agg,
        args.apikey,
    )
