import requests
import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from common.mocreo_auth import delete_v3_apikey_record, prompt_yes_no


def delete_apikey(token, asset_id, prefix, force=False):
    if not force:
        confirmed = prompt_yes_no(
            f"Do you want to delete API key prefix {prefix} from asset {asset_id}?",
            default=False,
        )
        if not confirmed:
            print("Deletion cancelled.")
            return

    url = f"https://api.mocreo.com/v1/assets/{asset_id}/apikeys/{prefix}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.delete(url, headers=headers)
        if r.status_code in (200, 204):
            removed_from_registry = delete_v3_apikey_record(asset_id, prefix)
            if removed_from_registry:
                print("Deleted API key and removed it from the local asset-scoped API key registry")
                return
            print(r.text)
        else:
            print(f"ERROR: {r.status_code} - {r.text}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True)
    parser.add_argument("--asset_id", required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--force", action="store_true", help="Skip interactive confirmation prompts")
    args = parser.parse_args()
    delete_apikey(args.token, args.asset_id, args.prefix, args.force)
