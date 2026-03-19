import sys
from pathlib import Path

import requests

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = Path(__file__).resolve().parents[3]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from common.mocreo_auth import (
    LEGACY_PASSWORD_KEYS,
    LEGACY_USER_KEYS,
    first_env_value,
    get_saved_v3_apikey_for_asset,
    load_env,
)
from v3_format_timestamps import build_timestamp_payload
from v3_get_asset_display_context import build_asset_display_context_payload


LOGIN_URL = "https://api.mocreo.com/v1/users/login"


def load_saved_credentials():
    load_env()
    return {
        "user": first_env_value("MOCREO_USER", *LEGACY_USER_KEYS),
        "password": first_env_value("MOCREO_PASS", *LEGACY_PASSWORD_KEYS),
    }


def login_with_saved_credentials():
    creds = load_saved_credentials()
    if not creds["user"] or not creds["password"]:
        print(
            "MOCREO_CREDENTIALS_MISSING: No credentials found in .env. Run the setup script to configure.",
            file=sys.stderr,
        )
        sys.exit(2)

    response = requests.post(
        LOGIN_URL,
        json={"email": creds["user"], "password": creds["password"]},
        headers={"Content-Type": "application/json", "Origin": "https://api.mocreo.com"},
    )
    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(1)
    result = response.json().get("result", {})
    token = result.get("access_token")
    if not token:
        print("ERROR: Login response did not contain access_token.", file=sys.stderr)
        sys.exit(1)
    return {
        "authValue": token,
        "isApiKey": False,
        "mode": "token",
        "source": "login",
        "tier": None,
        "permissions": None,
    }


def _make_apikey_auth(record):
    return {
        "authValue": record["key"],
        "isApiKey": True,
        "mode": "apikey",
        "source": "saved_apikey",
        "tier": record.get("tier"),
        "permissions": record.get("permissions", []),
        "prefix": record.get("prefix"),
    }


def resolve_read_auth(asset_id, required_permissions=None):
    permissions = required_permissions or ["device.read"]
    record = get_saved_v3_apikey_for_asset(
        asset_id=asset_id,
        required_permissions=permissions,
        preferred_tier="read",
    )
    if record and record.get("key"):
        return _make_apikey_auth(record)
    auth_info = login_with_saved_credentials()
    auth_info["source"] = "login_fallback"
    return auth_info


def resolve_write_auth(asset_id, required_permissions=None):
    permissions = required_permissions or ["device.update"]
    record = get_saved_v3_apikey_for_asset(
        asset_id=asset_id,
        required_permissions=permissions,
        preferred_tier="write",
    )
    if record and record.get("key"):
        return _make_apikey_auth(record)
    auth_info = login_with_saved_credentials()
    auth_info["source"] = "login_fallback"
    return auth_info


def resolve_auth_policy(policy, asset_id=None, required_permissions=None):
    normalized = (policy or "").strip().lower()
    if normalized in {"token-only", "token_first", "token-first", "export"}:
        auth_info = login_with_saved_credentials()
        auth_info["source"] = "login_policy"
        auth_info["policy"] = "export" if normalized == "export" else "token-only"
        return auth_info

    if normalized in {"asset-read", "read"}:
        if not asset_id:
            raise ValueError("asset_id is required for asset-read policy.")
        auth_info = resolve_read_auth(asset_id, required_permissions)
        auth_info["policy"] = "asset-read"
        return auth_info

    if normalized in {"asset-write", "write"}:
        if not asset_id:
            raise ValueError("asset_id is required for asset-write policy.")
        auth_info = resolve_write_auth(asset_id, required_permissions)
        auth_info["policy"] = "asset-write"
        return auth_info

    raise ValueError(f"Unsupported auth policy: {policy}")


def build_headers(auth_info):
    if auth_info["isApiKey"]:
        return {"X-API-Key": auth_info["authValue"]}
    return {"Authorization": f"Bearer {auth_info['authValue']}"}


def get_json(url, auth_info, params=None, allow_token_fallback=False):
    response = requests.get(url, headers=build_headers(auth_info), params=params)
    if response.status_code == 200:
        return response.json(), auth_info, []

    if allow_token_fallback and auth_info["isApiKey"] and response.status_code in {401, 500}:
        fallback_auth = login_with_saved_credentials()
        retry = requests.get(url, headers=build_headers(fallback_auth), params=params)
        if retry.status_code == 200:
            fallback_auth["policy"] = auth_info.get("policy")
            return (
                retry.json(),
                fallback_auth,
                [f"Fell back from saved API key to login token after API-key request failed with HTTP {response.status_code}."],
            )

    print(f"ERROR: {response.status_code} - {response.text}", file=sys.stderr)
    sys.exit(1)


def fetch_asset_display_context(asset_id, auth_info):
    payload, effective_auth, messages = get_json(
        f"https://api.mocreo.com/v1/assets/{asset_id}",
        auth_info,
        allow_token_fallback=True,
    )
    if auth_info.get("policy") and not effective_auth.get("policy"):
        effective_auth["policy"] = auth_info["policy"]
    context = build_asset_display_context_payload(payload, asset_id)
    context["messages"] = messages + context.get("messages", [])
    return context, effective_auth


def normalize_epoch_millis(value):
    if value is None:
        return None
    numeric = int(value)
    if abs(numeric) < 10_000_000_000:
        return numeric * 1000
    return numeric


def build_named_timestamp_payload(named_timestamps, tz_name, time_format):
    normalized = []
    labels = []
    for label, value in named_timestamps:
        ts_ms = normalize_epoch_millis(value)
        if ts_ms is None:
            continue
        labels.append((label, ts_ms))
        normalized.append(ts_ms)

    payload = build_timestamp_payload(normalized, tz_name, time_format)
    results_by_ts = {item["timestamp"]: item for item in payload.get("results", [])}
    named_results = []
    for label, ts_ms in labels:
        item = dict(results_by_ts.get(ts_ms, {"timestamp": ts_ms}))
        item["label"] = label
        named_results.append(item)

    payload["results"] = named_results
    return payload


def summarize_auth(auth_info):
    return {
        "mode": auth_info["mode"],
        "source": auth_info["source"],
        "policy": auth_info.get("policy"),
        "tier": auth_info.get("tier"),
        "permissions": auth_info.get("permissions"),
        "prefix": auth_info.get("prefix"),
    }
