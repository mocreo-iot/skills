import requests
import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from common.mocreo_auth import delete_env_keys, extract_apikey_prefix, get_saved_v3_apikey, prompt_yes_no


def delete_apikey(token, asset_id, prefix, force=False):
    saved_apikey = get_saved_v3_apikey()
    saved_prefix = extract_apikey_prefix(saved_apikey)
    is_default_key = saved_prefix == prefix and saved_prefix is not None

    if not force:
        if is_default_key:
            confirmed = prompt_yes_no(
                f"The API key prefix {prefix} matches the current default MOCREO_V3_API_KEY in .env. Do you want to delete it?",
                default=False,
            )
        else:
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
            if is_default_key:
                clear_saved = force or prompt_yes_no(
                    "Do you also want to clear MOCREO_V3_API_KEY from .env now that the default key was deleted?",
                    default=True,
                )
                if clear_saved:
                    delete_env_keys("MOCREO_V3_API_KEY")
                    print("Deleted API key and cleared MOCREO_V3_API_KEY from .env")
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
