import argparse
import json
import sys

from v3_auth_policy_helpers import resolve_auth_policy


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resolve Smart System auth according to a short-circuit policy")
    parser.add_argument("--policy", required=True, choices=["token-only", "asset-read", "asset-write", "export"])
    parser.add_argument("--asset_id")
    parser.add_argument("--permissions", default=None, help="Comma-separated required permissions")
    args = parser.parse_args()

    permissions = None
    if args.permissions:
        permissions = [item.strip() for item in args.permissions.split(",") if item.strip()]

    try:
        auth_info = resolve_auth_policy(args.policy, asset_id=args.asset_id, required_permissions=permissions)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    print(
        json.dumps(
            {
                "success": True,
                "auth": auth_info["authValue"],
                "apikey": auth_info["isApiKey"],
                "mode": auth_info["mode"],
                "source": auth_info["source"],
                "policy": auth_info.get("policy"),
                "tier": auth_info.get("tier"),
                "permissions": auth_info.get("permissions"),
                "prefix": auth_info.get("prefix"),
            },
            ensure_ascii=False,
        )
    )
