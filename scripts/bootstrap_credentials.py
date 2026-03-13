import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from common.mocreo_auth import resolve_credentials


def main():
    parser = argparse.ArgumentParser(description="Bootstrap shared MOCREO credentials")
    parser.add_argument("--platform", choices=["smart", "sensor"], default=None)
    args = parser.parse_args()

    creds = resolve_credentials(
        platform=args.platform,
        allow_prompt=True,
        persist_platform=True,
    )

    print(f"Saved credentials to {creds['env_path']}")
    print(f"Default platform: {creds['platform']}")
    print("Password was captured in the terminal with hidden input and stored only in the local .env file.")


if __name__ == "__main__":
    main()
