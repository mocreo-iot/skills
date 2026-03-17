import requests
import argparse
import sys
import json

SAFE_CONFIG_FIELDS = {"city", "tz", "country", "state"}


def update_asset_config(auth_val, asset_id, config_json, is_apikey=False):
    update_asset_config_with_mode(auth_val, asset_id, config_json, is_apikey, False)


def update_asset_config_with_mode(auth_val, asset_id, config_json, is_apikey=False, safe_mode=False):
    url = f"https://api.mocreo.com/v1/assets/{asset_id}/config"
    headers = {"X-API-Key": auth_val} if is_apikey else {"Authorization": f"Bearer {auth_val}"}
    headers["Content-Type"] = "application/json"
    try:
        payload = json.loads(config_json)
        if safe_mode:
            payload = {key: value for key, value in payload.items() if key in SAFE_CONFIG_FIELDS}
            if not payload:
                print(
                    "ERROR: Safe mode only allows these top-level fields: "
                    f"{', '.join(sorted(SAFE_CONFIG_FIELDS))}",
                    file=sys.stderr,
                )
                sys.exit(1)
        r = requests.patch(url, json=payload, headers=headers)
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
    parser.add_argument("--config", required=True)
    parser.add_argument("--apikey", action="store_true")
    parser.add_argument(
        "--safe",
        action="store_true",
        help="Allow only stable top-level fields: city, tz, country, state",
    )
    args = parser.parse_args()
    update_asset_config_with_mode(args.auth, args.asset_id, args.config, args.apikey, args.safe)
