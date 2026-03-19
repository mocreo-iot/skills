import argparse
import json
import sys
from datetime import datetime, timezone

try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except ImportError:  # pragma: no cover
    ZoneInfo = None
    ZoneInfoNotFoundError = Exception


def build_timestamp_payload(timestamps, tz_name, time_format):
    fmt = "%m/%d/%Y %I:%M:%S %p" if time_format == "hour12" else "%Y-%m-%d %H:%M:%S"
    payload = {
        "success": True,
        "requestedTz": tz_name,
        "timeFormat": time_format,
        "results": [],
        "messages": [],
        "errors": [],
    }

    if ZoneInfo is None:
        payload["success"] = False
        payload["errors"].append("ZONEINFO_UNAVAILABLE")
    else:
        try:
            zone = ZoneInfo(tz_name)
        except ZoneInfoNotFoundError:
            zone = None
            payload["success"] = False
            payload["errors"].append("TIMEZONE_DATA_UNAVAILABLE")
            payload["messages"].append(
                f"Could not load timezone '{tz_name}' on this machine. Returning UTC timestamps instead."
            )

    for raw in timestamps:
        ts_ms = int(raw)
        utc_dt = datetime.fromtimestamp(ts_ms / 1000, timezone.utc)
        item = {
            "timestamp": ts_ms,
            "utc": utc_dt.strftime("%Y-%m-%d %H:%M:%S UTC"),
        }
        if payload["success"]:
            local_dt = utc_dt.astimezone(zone)
            item["formatted"] = local_dt.strftime(fmt)
        payload["results"].append(item)

    return payload


def format_timestamps(timestamps, tz_name, time_format):
    print(json.dumps(build_timestamp_payload(timestamps, tz_name, time_format), ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Format epoch-millisecond timestamps for user-facing output")
    parser.add_argument("--tz", required=True)
    parser.add_argument("--time_format", choices=["hour12", "hour24"], default="hour24")
    parser.add_argument("--timestamps", nargs="+", required=True)
    args = parser.parse_args()
    try:
        format_timestamps(args.timestamps, args.tz, args.time_format)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
