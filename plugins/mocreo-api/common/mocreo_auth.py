import argparse
import getpass
import json
import os
from pathlib import Path

from dotenv import load_dotenv


def resolve_runtime_root():
    repo_root = Path(__file__).resolve().parents[1]
    parent = repo_root.parent
    grandparent = parent.parent

    # Marketplace deployment layout is:
    # <marketplace-root>/plugins/<plugin-name>/...
    # Shared runtime files should live at the marketplace root.
    if parent.name == "plugins" and (grandparent / ".claude-plugin" / "marketplace.json").exists():
        return grandparent

    return repo_root


ROOT_DIR = resolve_runtime_root()
ENV_PATH = ROOT_DIR / ".env"
V3_APIKEY_REGISTRY_PATH = ROOT_DIR / ".mocreo_v3_apikeys.json"
VALID_PLATFORMS = {"sensor", "smart"}
LEGACY_USER_KEYS = ("MOCREO_V2_USER", "MOCREO_V3_EMAIL")
LEGACY_PASSWORD_KEYS = ("MOCREO_V2_PASS", "MOCREO_V3_PASS")
SENSOR_APP_LABEL = "MOCREO Sensor App / Sensor System / V2"
SMART_APP_LABEL = "MOCREO Smart App / Smart System / V3"
V2_HUBS = ("H1", "H2")
V3_HUBS = ("H3", "H5-Lite", "H5-Pro", "H6-Lite", "H6-Pro")
V2_ONLY_SENSORS = ("ST1", "ST2", "ST3", "ST4", "ST7", "ST7-CL", "SS1", "NM1")
V3_ONLY_SENSORS = ("MS2", "LS1", "LS2", "LS3", "LW1", "LD1", "LB1", "NS1", "NS2", "NS3")
SHARED_SENSORS = ("ST5", "ST6", "ST8", "ST9", "ST10", "MS1", "SW2")


def load_env():
    load_dotenv(ENV_PATH)


def prompt_if_missing(prompt_text, secret=False):
    if secret:
        return getpass.getpass(prompt_text).strip()
    return input(prompt_text).strip()


def prompt_yes_no(prompt_text, default=False):
    suffix = "[Y/n]" if default else "[y/N]"
    while True:
        answer = input(f"{prompt_text} {suffix}: ").strip().lower()
        if not answer:
            return default
        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False
        print("Please answer yes or no.")


def first_env_value(*keys):
    for key in keys:
        value = os.getenv(key)
        if value:
            return value
    return None


def infer_legacy_platform():
    has_v2 = bool(first_env_value("MOCREO_V2_USER", "MOCREO_V2_PASS"))
    has_v3 = bool(first_env_value("MOCREO_V3_EMAIL", "MOCREO_V3_PASS"))
    if has_v2 and not has_v3:
        return "sensor"
    if has_v3 and not has_v2:
        return "smart"
    return None


def write_env_values(values):
    existing = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            existing[key] = value

    for legacy_key in LEGACY_USER_KEYS + LEGACY_PASSWORD_KEYS:
        existing.pop(legacy_key, None)

    existing.update({k: v for k, v in values.items() if v is not None})

    ordered_keys = [
        "MOCREO_USER",
        "MOCREO_PASS",
        "MOCREO_PLATFORM",
    ]

    rendered = []
    for key in ordered_keys:
        if key in existing:
            rendered.append(f"{key}={existing[key]}")

    remaining = sorted(k for k in existing if k not in ordered_keys)
    rendered.extend(f"{key}={existing[key]}" for key in remaining)
    ENV_PATH.write_text("\n".join(rendered) + "\n", encoding="utf-8")


def delete_env_keys(*keys):
    existing = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            existing[key] = value

    for key in keys:
        existing.pop(key, None)

    ordered_keys = [
        "MOCREO_USER",
        "MOCREO_PASS",
        "MOCREO_PLATFORM",
    ]

    rendered = []
    for key in ordered_keys:
        if key in existing:
            rendered.append(f"{key}={existing[key]}")

    remaining = sorted(k for k in existing if k not in ordered_keys)
    rendered.extend(f"{key}={existing[key]}" for key in remaining)
    ENV_PATH.write_text("\n".join(rendered) + "\n", encoding="utf-8")


def normalize_platform(value):
    if not value:
        return None
    normalized = value.strip().lower()
    if normalized in VALID_PLATFORMS:
        return normalized
    return None


def extract_apikey_prefix(api_key):
    if not api_key:
        return None
    parts = api_key.strip().split("_", 2)
    if len(parts) != 3 or parts[0] != "mok":
        return None
    return parts[1]


def load_v3_apikey_registry():
    if not V3_APIKEY_REGISTRY_PATH.exists():
        return {"assets": {}}
    try:
        data = json.loads(V3_APIKEY_REGISTRY_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"assets": {}}
    if not isinstance(data, dict):
        return {"assets": {}}
    assets = data.get("assets")
    if not isinstance(assets, dict):
        data["assets"] = {}
    return data


def save_v3_apikey_registry(registry):
    rendered = json.dumps(registry, indent=2, ensure_ascii=False) + "\n"
    V3_APIKEY_REGISTRY_PATH.write_text(rendered, encoding="utf-8")


def normalize_permissions_list(permissions):
    unique = []
    for permission in permissions or []:
        normalized = (permission or "").strip()
        if normalized and normalized not in unique:
            unique.append(normalized)
    return sorted(unique)


def make_permission_signature(permissions):
    normalized = normalize_permissions_list(permissions)
    return ",".join(normalized) if normalized else "unspecified"


def classify_v3_apikey_tier(permissions):
    normalized = normalize_permissions_list(permissions)
    if any(permission.endswith(".update") or permission.endswith(".delete") for permission in normalized):
        return "write"
    return "read"


def save_v3_apikey_record(asset_id, asset_name, api_key, permissions, prefix=None, display_name=None, created_at=None, expires_at=None):
    if not asset_id or not api_key:
        return
    registry = load_v3_apikey_registry()
    assets = registry.setdefault("assets", {})
    asset_entry = assets.setdefault(asset_id, {"assetName": asset_name or "", "keys": {}})
    if asset_name:
        asset_entry["assetName"] = asset_name
    normalized_permissions = normalize_permissions_list(permissions)
    signature = make_permission_signature(normalized_permissions)
    asset_entry.setdefault("keys", {})[signature] = {
        "prefix": prefix or extract_apikey_prefix(api_key),
        "key": api_key,
        "permissions": normalized_permissions,
        "tier": classify_v3_apikey_tier(normalized_permissions),
        "displayName": display_name,
        "createdAt": created_at,
        "expiresAt": expires_at,
    }
    save_v3_apikey_registry(registry)


def delete_v3_apikey_record(asset_id, prefix):
    if not asset_id or not prefix:
        return False
    registry = load_v3_apikey_registry()
    assets = registry.get("assets", {})
    asset_entry = assets.get(asset_id)
    if not asset_entry:
        return False
    keys = asset_entry.get("keys", {})
    removed = False
    for signature, record in list(keys.items()):
        if isinstance(record, dict) and record.get("prefix") == prefix:
            keys.pop(signature, None)
            removed = True
    if not keys:
        assets.pop(asset_id, None)
    if removed:
        save_v3_apikey_registry(registry)
    return removed


def get_saved_v3_apikey_for_asset(asset_id, required_permissions=None, preferred_tier=None):
    if not asset_id:
        return None
    registry = load_v3_apikey_registry()
    asset_entry = registry.get("assets", {}).get(asset_id)
    if not asset_entry:
        return None
    required = set(normalize_permissions_list(required_permissions))
    candidates = []
    for record in asset_entry.get("keys", {}).values():
        if not isinstance(record, dict) or not record.get("key"):
            continue
        permissions = set(normalize_permissions_list(record.get("permissions")))
        if required and not required.issubset(permissions):
            continue
        candidates.append(record)
    if not candidates:
        return None
    if preferred_tier:
        tier_matches = [record for record in candidates if record.get("tier") == preferred_tier]
        if tier_matches:
            candidates = tier_matches
    candidates.sort(key=lambda record: (record.get("tier") != "write", len(record.get("permissions", []))))
    return candidates[0]


def prompt_choice(prompt_text, options):
    print(prompt_text)
    for index, (_, label) in enumerate(options, start=1):
        print(f"{index}. {label}")
    while True:
        choice = input(f"Enter 1-{len(options)}: ").strip()
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(options):
                return options[index - 1][0]
        print(f"Invalid selection. Enter a number between 1 and {len(options)}.")


def choose_platform_by_questions():
    known_item = prompt_choice(
        "How would you like to identify your MOCREO system?",
        [
            ("app", "I know which app/system I use"),
            ("hub", "I know the Hub model"),
            ("sensor", "I know the Sensor model"),
            ("account", "I only know my account and need guidance"),
        ],
    )

    if known_item == "app":
        return prompt_choice(
            "Which app/system do you use?",
            [
                ("sensor", SENSOR_APP_LABEL),
                ("smart", SMART_APP_LABEL),
            ],
        )

    if known_item == "hub":
        hub_family = prompt_choice(
            "Which Hub family matches your device?",
            [
                ("sensor", f"{', '.join(V2_HUBS)} ({SENSOR_APP_LABEL})"),
                ("smart", f"{', '.join(V3_HUBS)} ({SMART_APP_LABEL})"),
                ("unknown", "I am still not sure"),
            ],
        )
        if hub_family != "unknown":
            return hub_family
        return prompt_choice(
            "If the Hub model is unclear, which app did you register it in?",
            [
                ("sensor", SENSOR_APP_LABEL),
                ("smart", SMART_APP_LABEL),
            ],
        )

    if known_item == "sensor":
        sensor_family = prompt_choice(
            "Which Sensor family matches your device?",
            [
                ("sensor", f"V2-only sensors: {', '.join(V2_ONLY_SENSORS)}"),
                ("smart", f"V3-only sensors: {', '.join(V3_ONLY_SENSORS)}"),
                ("shared", f"Shared sensors used by both systems: {', '.join(SHARED_SENSORS)}"),
            ],
        )
        if sensor_family in VALID_PLATFORMS:
            return sensor_family
        follow_up = prompt_choice(
            "That sensor model works on both systems. What else do you know?",
            [
                ("sensor_app", SENSOR_APP_LABEL),
                ("smart_app", SMART_APP_LABEL),
                ("sensor_hub", f"My Hub is one of: {', '.join(V2_HUBS)}"),
                ("smart_hub", f"My Hub is one of: {', '.join(V3_HUBS)}"),
            ],
        )
        return "sensor" if follow_up in {"sensor_app", "sensor_hub"} else "smart"

    return prompt_choice(
        "Which statement sounds closer to your setup?",
        [
            ("sensor", "I use hubs like H1/H2 with sensor nodes in the MOCREO Sensor App"),
            ("smart", "I use H3/H5/H6 or NS series devices in the MOCREO Smart App"),
        ],
    )


def resolve_credentials(platform=None, allow_prompt=True, persist_platform=True):
    load_env()
    username = first_env_value("MOCREO_USER", *LEGACY_USER_KEYS)
    password = first_env_value("MOCREO_PASS", *LEGACY_PASSWORD_KEYS)
    saved_platform = normalize_platform(os.getenv("MOCREO_PLATFORM")) or infer_legacy_platform()
    target_platform = normalize_platform(platform) or saved_platform

    if not username and not allow_prompt:
        raise ValueError("Missing MOCREO_USER")
    if not password and not allow_prompt:
        raise ValueError("Missing MOCREO_PASS")

    updates = {}
    if username and not os.getenv("MOCREO_USER"):
        updates["MOCREO_USER"] = username
    if password and not os.getenv("MOCREO_PASS"):
        updates["MOCREO_PASS"] = password
    if not username and allow_prompt:
        username = prompt_if_missing("Enter your MOCREO account email: ")
        updates["MOCREO_USER"] = username
    if not password and allow_prompt:
        password = prompt_if_missing("Enter your MOCREO password (input hidden): ", secret=True)
        updates["MOCREO_PASS"] = password
    if not target_platform and allow_prompt and persist_platform:
        target_platform = choose_platform_by_questions()
        updates["MOCREO_PLATFORM"] = target_platform
    elif target_platform and target_platform != normalize_platform(os.getenv("MOCREO_PLATFORM")) and persist_platform:
        updates["MOCREO_PLATFORM"] = target_platform

    if updates:
        write_env_values(updates)
        load_env()

    return {
        "user": username,
        "password": password,
        "platform": target_platform,
        "env_path": str(ENV_PATH),
    }


def add_shared_auth_args(parser: argparse.ArgumentParser, platform_help: str):
    load_env()
    parser.add_argument("--user", default=first_env_value("MOCREO_USER", *LEGACY_USER_KEYS))
    parser.add_argument("--password", default=first_env_value("MOCREO_PASS", *LEGACY_PASSWORD_KEYS))
    parser.add_argument(
        "--platform",
        choices=["sensor", "smart"],
        default=normalize_platform(os.getenv("MOCREO_PLATFORM")) or infer_legacy_platform(),
        help=platform_help,
    )


def build_credentials_from_args(args, fallback_platform):
    explicit_platform = normalize_platform(getattr(args, "platform", None))
    saved_platform = normalize_platform(os.getenv("MOCREO_PLATFORM")) or infer_legacy_platform()
    if getattr(args, "user", None) and getattr(args, "password", None):
        effective_platform = explicit_platform or saved_platform or fallback_platform
        write_env_values(
            {
                "MOCREO_USER": args.user,
                "MOCREO_PASS": args.password,
                "MOCREO_PLATFORM": effective_platform,
            }
        )
        load_env()
        return {
            "user": args.user,
            "password": args.password,
            "platform": effective_platform,
            "env_path": str(ENV_PATH),
        }

    creds = resolve_credentials(
        platform=explicit_platform,
        allow_prompt=True,
        persist_platform=True,
    )
    if not creds["platform"]:
        creds["platform"] = fallback_platform
        write_env_values({"MOCREO_PLATFORM": creds["platform"]})
        load_env()
    return creds
