import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from common.mocreo_auth import get_saved_v3_apikey_for_asset


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resolve the best saved Smart System API key for an asset")
    parser.add_argument("--asset_id", required=True)
    parser.add_argument("--permissions", default=None, help="Comma-separated required permissions")
    parser.add_argument("--tier", choices=["read", "write"], default=None)
    args = parser.parse_args()

    required_permissions = None
    if args.permissions:
        required_permissions = [item.strip() for item in args.permissions.split(",") if item.strip()]

    record = get_saved_v3_apikey_for_asset(
        asset_id=args.asset_id,
        required_permissions=required_permissions,
        preferred_tier=args.tier,
    )
    if not record:
        print(json.dumps({"found": False}))
        sys.exit(1)

    payload = {"found": True}
    payload.update(record)
    print(json.dumps(payload, ensure_ascii=False))
