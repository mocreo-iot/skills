import argparse
import json

from v3_auth_policy_helpers import (
    fetch_asset_display_context,
    get_json,
    resolve_auth_policy,
    summarize_auth,
)
from v3_format_timestamps import build_timestamp_payload


VALID_FIELDS = {"temperature", "humidity", "water_leak", "water_level", "frozen"}


def get_device_history_auto(asset_id, device_id, start, end, field, limit=None, window=None, agg=None, tz_override=None):
    if field not in VALID_FIELDS:
        raise ValueError(f"Invalid field '{field}'. Valid values: {', '.join(sorted(VALID_FIELDS))}")
    if agg and not window:
        raise ValueError("--agg requires --window.")
    if limit is not None and (window or agg):
        raise ValueError("--limit cannot be combined with --window/--agg.")

    auth_info = resolve_auth_policy(
        "asset-read",
        asset_id=asset_id,
        required_permissions=["device.read"],
    )
    display_context, auth_info = fetch_asset_display_context(asset_id, auth_info)
    tz_name = tz_override or display_context["result"].get("tz") or "UTC"
    params = {"from": start, "to": end, "tz": tz_name, "field": field}
    if window:
        params["windowDuration"] = window
    if agg:
        params["aggregationsType"] = agg
    if limit is not None:
        params["limit"] = limit

    history_payload, auth_info, retry_messages = get_json(
        f"https://api.mocreo.com/v1/assets/{asset_id}/devices/{device_id}/history",
        auth_info,
        params=params,
        allow_token_fallback=True,
    )
    history_result = history_payload.get("result") or {}
    rows = history_result.get("data") or []
    formatted = build_timestamp_payload(
        [row["time"] for row in rows if isinstance(row, dict) and row.get("time") is not None],
        tz_name,
        display_context["result"].get("timeFormat") or "hour24",
    )

    print(
        json.dumps(
            {
                "success": True,
                "auth": summarize_auth(auth_info),
                "assetDisplayContext": display_context["result"],
                "query": {
                    "assetId": asset_id,
                    "deviceId": device_id,
                    "field": field,
                    "from": int(start),
                    "to": int(end),
                    "tz": tz_name,
                    "limit": limit,
                    "windowDuration": window,
                    "aggregationsType": agg,
                },
                "history": history_result,
                "formattedTimestamps": formatted,
                "messages": display_context.get("messages", []) + retry_messages + history_payload.get("messages", []),
                "errors": display_context.get("errors", []) + history_payload.get("errors", []),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get Smart System device history with short-circuit auth resolution")
    parser.add_argument("--asset_id", required=True)
    parser.add_argument("--device_id", required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--field", required=True)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--window", "--window_duration", dest="window")
    parser.add_argument("--agg", "--aggregations_type", dest="agg")
    parser.add_argument("--tz", default=None)
    args = parser.parse_args()
    try:
        get_device_history_auto(
            args.asset_id,
            args.device_id,
            args.start,
            args.end,
            args.field,
            limit=args.limit,
            window=args.window,
            agg=args.agg,
            tz_override=args.tz,
        )
    except ValueError as exc:
        raise SystemExit(f"ERROR: {exc}")
