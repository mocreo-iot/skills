import json
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = REPO_ROOT / "plugins" / "mocreo-api"
IGNORE_PATTERNS = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo")
PACKAGE_NOTICE = """# Generated Package

This directory is a generated Claude marketplace package.

Do not edit files in this directory directly. Update the canonical source files in the repository root and regenerate this package with:

```bash
python scripts/build_claude_plugin.py
```
"""

PLUGIN_MANIFEST = {
    "name": "mocreo-api",
    "version": "1.0.0",
    "description": "MOCREO API toolkit for AI agents. Interact with MOCREO IoT sensors and smart devices via natural language.",
    "author": {
        "name": "MOCREO",
    },
    "repository": "https://github.com/mocreo-iot/skills",
    "license": "MIT",
    "keywords": ["mocreo", "iot", "sensor", "smart", "devices"],
    "skills": "./skills/mocreo-api",
}

DIRECTORY_COPIES = [
    ("common", "common"),
    ("skills/mocreo-api", "skills/mocreo-api"),
    ("skills/mocreo-sensor-system", "skills/mocreo-sensor-system"),
    ("skills/mocreo-smart-system", "skills/mocreo-smart-system"),
]

FILE_COPIES = [
    ("scripts/setup_credentials.py", "scripts/setup_credentials.py"),
    ("requirements.txt", "requirements.txt"),
    (".env.example", ".env.example"),
    (".claude-plugin/openapi.en.yaml", "openapi.en.yaml"),
    (".claude-plugin/openapi.zh.yaml", "openapi.zh.yaml"),
    (".claude-plugin/sensor-swagger.json", "sensor-swagger.json"),
]

REQUIRED_OUTPUTS = [
    ".claude-plugin/plugin.json",
    "skills/mocreo-api/SKILL.md",
    "skills/mocreo-sensor-system/SKILL.md",
    "skills/mocreo-smart-system/SKILL.md",
    "scripts/setup_credentials.py",
    "common/mocreo_auth.py",
    "openapi.en.yaml",
    "openapi.zh.yaml",
    "sensor-swagger.json",
    "README.generated.md",
]

BANNED_OUTPUTS = [
    ".env",
    ".mocreo_v3_apikeys.json",
]


def ensure_exists(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Required source path is missing: {path}")


def copy_tree(src_rel: str, dst_rel: str) -> None:
    src = REPO_ROOT / src_rel
    dst = PACKAGE_ROOT / dst_rel
    ensure_exists(src)
    if dst.exists():
        shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, ignore=IGNORE_PATTERNS)


def copy_file(src_rel: str, dst_rel: str) -> None:
    src = REPO_ROOT / src_rel
    dst = PACKAGE_ROOT / dst_rel
    ensure_exists(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def write_plugin_manifest() -> None:
    manifest_path = PACKAGE_ROOT / ".claude-plugin" / "plugin.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(PLUGIN_MANIFEST, indent=2) + "\n",
        encoding="utf-8",
    )


def write_package_notice() -> None:
    notice_path = PACKAGE_ROOT / "README.generated.md"
    notice_path.write_text(PACKAGE_NOTICE, encoding="utf-8")


def validate_package() -> None:
    missing = [path for path in REQUIRED_OUTPUTS if not (PACKAGE_ROOT / path).exists()]
    if missing:
        raise FileNotFoundError(
            "Generated package is missing required files: " + ", ".join(missing)
        )

    present_banned = [path for path in BANNED_OUTPUTS if (PACKAGE_ROOT / path).exists()]
    if present_banned:
        raise RuntimeError(
            "Generated package contains banned local runtime files: "
            + ", ".join(present_banned)
        )

    pycache_entries = list(PACKAGE_ROOT.rglob("__pycache__"))
    if pycache_entries:
        raise RuntimeError(
            "Generated package contains __pycache__ directories: "
            + ", ".join(str(path.relative_to(PACKAGE_ROOT)) for path in pycache_entries)
        )

    pyc_entries = list(PACKAGE_ROOT.rglob("*.pyc"))
    if pyc_entries:
        raise RuntimeError(
            "Generated package contains compiled Python files: "
            + ", ".join(str(path.relative_to(PACKAGE_ROOT)) for path in pyc_entries)
        )


def main() -> None:
    if PACKAGE_ROOT.exists():
        shutil.rmtree(PACKAGE_ROOT)

    for src_rel, dst_rel in DIRECTORY_COPIES:
        copy_tree(src_rel, dst_rel)

    for src_rel, dst_rel in FILE_COPIES:
        copy_file(src_rel, dst_rel)

    write_plugin_manifest()
    write_package_notice()
    validate_package()
    print(f"Generated Claude plugin package at {PACKAGE_ROOT}")


if __name__ == "__main__":
    main()
