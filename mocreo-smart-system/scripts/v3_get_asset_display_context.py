import argparse
import json
import sys

import requests


def _codepoints(value):
    return [f"U+{ord(ch):04X}" for ch in value or ""]


def normalize_temperature_unit(raw_value):
    raw_value = raw_value or ""
    stripped = raw_value.strip()
    normalized_upper = stripped.upper()
    code_points = _codepoints(stripped)
    code_point_set = set(code_points)

    fahrenheit_tokens = {"F", "°F", "℉", "FAHRENHEIT"}
    celsius_tokens = {"C", "°C", "℃", "CELSIUS"}

    if stripped in fahrenheit_tokens or normalized_upper in fahrenheit_tokens or "U+2109" in code_point_set:
        return {
            "raw": raw_value,
            "codePoints": code_points,
            "trusted": True,
            "canonical": "fahrenheit",
            "display": "°F",
            "reason": "Matched Fahrenheit by literal token or Unicode code point.",
        }

    if stripped in celsius_tokens or normalized_upper in celsius_tokens or "U+2103" in code_point_set:
        return {
            "raw": raw_value,
            "codePoints": code_points,
            "trusted": True,
            "canonical": "celsius",
            "display": "°C",
            "reason": "Matched Celsius by literal token or Unicode code point.",
        }

    return {
        "raw": raw_value,
        "codePoints": code_points,
        "trusted": False,
        "canonical": "unknown",
        "display": None,
        "reason": "Could not map the unit to Celsius or Fahrenheit without guessing.",
    }


def get_asset_display_context(auth_val, asset_id, is_apikey=False):
    url = f"https://api.mocreo.com/v1/assets/{asset_id}"
    headers = {"X-API-Key": auth_val} if is_apikey else {"Authorization": f"Bearer {auth_val}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
            sys.exit(1)

        payload = response.json()
        result = payload.get("result") or {}
        config = result.get("config") or {}
        units = config.get("units") or {}
        print(json.dumps(build_asset_display_context_payload(payload, asset_id)))
    except Exception as exc:
        print(f"EXCEPTION: {exc}", file=sys.stderr)
        sys.exit(1)


def build_asset_display_context_payload(payload, asset_id):
    result = payload.get("result") or {}
    config = result.get("config") or {}
    units = config.get("units") or {}
    temp_unit = normalize_temperature_unit(units.get("temperature"))

    return {
        "success": True,
        "result": {
            "assetId": result.get("id") or result.get("_id") or asset_id,
            "displayName": result.get("displayName"),
            "tz": config.get("tz"),
            "timeFormat": config.get("timeFormat"),
            "temperatureUnit": temp_unit,
            "humidityUnit": units.get("humidity"),
        },
        "messages": payload.get("messages", []),
        "errors": payload.get("errors", []),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch asset display context with normalized temperature unit metadata")
    parser.add_argument("--auth", required=True)
    parser.add_argument("--asset_id", required=True)
    parser.add_argument("--apikey", action="store_true")
    args = parser.parse_args()
    get_asset_display_context(args.auth, args.asset_id, args.apikey)
