import argparse
import json

from v3_auth_policy_helpers import (
    build_named_timestamp_payload,
    fetch_asset_display_context,
    get_json,
    resolve_auth_policy,
    summarize_auth,
)


def get_device_details_auto(asset_id, device_id):
    auth_info = resolve_auth_policy(
        "asset-read",
        asset_id=asset_id,
        required_permissions=["device.read"],
    )
    display_context, auth_info = fetch_asset_display_context(asset_id, auth_info)
    device_payload, auth_info, retry_messages = get_json(
        f"https://api.mocreo.com/v1/assets/{asset_id}/devices/{device_id}",
        auth_info,
        allow_token_fallback=True,
    )
    device_result = device_payload.get("result") or {}
    attributes = device_result.get("attributes") or {}
    properties = device_result.get("properties") or {}
    timestamp_payload = build_named_timestamp_payload(
        [
            ("device.updatedAt", device_result.get("updatedAt")),
            ("device.properties.updatedAt", properties.get("updatedAt")),
            ("device.attributes.lastOnline", attributes.get("lastOnline")),
        ],
        display_context["result"].get("tz") or "UTC",
        display_context["result"].get("timeFormat") or "hour24",
    )

    print(
        json.dumps(
            {
                "success": True,
                "auth": summarize_auth(auth_info),
                "assetDisplayContext": display_context["result"],
                "device": device_result,
                "formattedTimestamps": timestamp_payload,
                "messages": display_context.get("messages", []) + retry_messages + device_payload.get("messages", []),
                "errors": display_context.get("errors", []) + device_payload.get("errors", []),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get Smart System device details with short-circuit auth resolution")
    parser.add_argument("--asset_id", required=True)
    parser.add_argument("--device_id", required=True)
    args = parser.parse_args()
    get_device_details_auto(args.asset_id, args.device_id)
