#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 - "$ROOT" "$@" <<'PY'
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise SystemExit("Missing Python dependency: PyYAML") from exc

ROOT = Path(sys.argv[1]).resolve()
ARGS = sys.argv[2:]
MANIFEST = Path(os.environ.get("GINFLOW_INSTALL_MANIFEST", str(ROOT / ".ginflow-install.json"))).expanduser().resolve()
VERSION = 1
PROFILE_RE = re.compile(r"^\s*[◆*]?([A-Za-z0-9][A-Za-z0-9._-]*)\s+")


def fail(message: str) -> None:
    print(f"❌ {message}", file=sys.stderr)
    raise SystemExit(1)


def info(message: str) -> None:
    print(f"ℹ️  {message}")


def ok(message: str) -> None:
    print(f"✅ {message}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    if path.is_dir():
        for item in sorted(path.rglob("*")):
            if item.is_file() and "__pycache__" not in item.parts and item.suffix != ".pyc":
                digest.update(str(item.relative_to(path)).encode())
                digest.update(item.read_bytes())
    else:
        digest.update(path.read_bytes())
    return digest.hexdigest()


def copy_tree(source: Path, destination: Path) -> None:
    ignored = shutil.ignore_patterns("__pycache__", "*.pyc", ".git", ".DS_Store")
    temporary = Path(tempfile.mkdtemp(prefix=f".{destination.name}.", dir=str(destination.parent)))
    try:
        shutil.copytree(source, temporary / destination.name, ignore=ignored)
        os.replace(temporary / destination.name, destination)
    finally:
        shutil.rmtree(temporary, ignore_errors=True)


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def backup_path(destination: Path) -> Path:
    return destination.with_name(destination.name + ".bak.ginflow-install")


def backup_existing(destination: Path) -> str | None:
    if not destination.exists() and not destination.is_symlink():
        return None
    backup = backup_path(destination)
    if backup.exists() or backup.is_symlink():
        fail(f"backup already exists; uninstall first or resolve manually: {backup}")
    if destination.is_symlink():
        backup.symlink_to(os.readlink(destination), target_is_directory=destination.is_dir())
    elif destination.is_dir():
        shutil.copytree(destination, backup, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    else:
        shutil.copy2(destination, backup)
    return str(backup)


def discover_profiles(profiles_dir: Path) -> list[tuple[str, Path]]:
    try:
        result = subprocess.run(["hermes", "profile", "list"], text=True, capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        fail(f"unable to discover Hermes profiles: {exc}")
    names = []
    for line in result.stdout.splitlines():
        match = PROFILE_RE.match(line)
        if match and match.group(1) != "Profile" and match.group(1) not in names:
            names.append(match.group(1))
    profiles = []
    for name in names:
        directory = profiles_dir / name
        if directory.is_dir() and (directory / "config.yaml").is_file():
            profiles.append((name, directory))
        else:
            info(f"skipping {name}: no native profile config directory")
    if not profiles:
        fail(f"no installed Hermes profile directories found under {profiles_dir}")
    return profiles


def update_config(config_path: Path) -> tuple[str, str, str]:
    original = config_path.read_bytes()
    backup = backup_existing(config_path)
    config = yaml.safe_load(original) or {}
    if not isinstance(config, dict):
        fail(f"profile config is not a YAML mapping: {config_path}")

    def mapping(parent: dict[str, Any], key: str) -> dict[str, Any]:
        value = parent.get(key)
        if not isinstance(value, dict):
            value = {}
            parent[key] = value
        return value

    def list_value(parent: dict[str, Any], key: str) -> list[Any]:
        value = parent.get(key)
        if not isinstance(value, list):
            value = []
            parent[key] = value
        return value

    external = list_value(mapping(config, "skills"), "external_dirs")
    setup_skills = str(ROOT / "skills")
    if setup_skills not in external:
        external.append(setup_skills)
    enabled = list_value(mapping(config, "plugins"), "enabled")
    if "ginflow-gate" not in enabled:
        enabled.append("ginflow-gate")
    rendered = yaml.safe_dump(config, sort_keys=False).encode()
    temporary = config_path.with_name(config_path.name + ".ginflow-install.tmp")
    temporary.write_bytes(rendered)
    os.replace(temporary, config_path)
    return sha256(config_path), sha256(Path(config_path)), backup or ""


def write_manifest(manifest: dict[str, Any]) -> None:
    temporary = MANIFEST.with_name(MANIFEST.name + ".tmp")
    temporary.write_text(json.dumps(manifest, indent=2) + "\n")
    os.replace(temporary, MANIFEST)


def install() -> None:
    if MANIFEST.exists():
        info("existing Ginflow installation found; cleaning it before reinstall")
        uninstall()
    source_skill = ROOT / "skills/ginflow"
    source_plugin = ROOT / "plugins/ginflow-gate"
    if not source_skill.is_dir() or not source_plugin.is_dir():
        fail("setup-repo skill or plugin source directory is missing")

    real_home = Path(os.environ.get("HERMES_REAL_HOME", str(Path.home()))).expanduser().resolve()
    profiles_dir = Path(os.environ.get("HERMES_PROFILES_DIR", str(real_home / ".hermes/profiles"))).expanduser().resolve()
    universal = real_home / ".agent/skills/ginflow"
    profiles = discover_profiles(profiles_dir)

    destinations = [universal] + [profile_dir / "plugins/ginflow-gate" for _, profile_dir in profiles]
    for destination in destinations:
        if destination.exists() and not destination.is_dir():
            fail(f"managed destination is not a directory: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if backup_path(destination).exists():
            fail(f"backup already exists; resolve before install: {backup_path(destination)}")

    manifest: dict[str, Any] = {
        "version": VERSION,
        "source_root": str(ROOT),
        "universal_skill": {"path": str(universal), "source": str(source_skill), "backup": None},
        "profiles": {},
    }
    try:
        universal_backup = backup_existing(universal)
        manifest["universal_skill"]["backup"] = universal_backup
        if universal.exists() or universal.is_symlink():
            remove_path(universal)
        copy_tree(source_skill, universal)
        manifest["universal_skill"]["installed_hash"] = sha256(universal)

        for name, profile_dir in profiles:
            plugin = profile_dir / "plugins/ginflow-gate"
            config = profile_dir / "config.yaml"
            plugin_backup = backup_existing(plugin)
            if plugin.exists() or plugin.is_symlink():
                remove_path(plugin)
            copy_tree(source_plugin, plugin)
            pre_config_hash = sha256(config)
            post_config_hash, _, config_backup = update_config(config)
            manifest["profiles"][name] = {
                "profile_dir": str(profile_dir),
                "plugin": str(plugin),
                "plugin_hash": sha256(plugin),
                "plugin_backup": plugin_backup,
                "config": str(config),
                "config_before_hash": pre_config_hash,
                "config_after_hash": post_config_hash,
                "config_backup": config_backup or None,
            }
            ok(f"{name}: Ginflow skill/plugin/config installed")
        write_manifest(manifest)
        ok(f"universal skill installed at {universal}")
        ok(f"manifest written to {MANIFEST}")
    except Exception:
        print("❌ installation failed; restoring destinations", file=sys.stderr)
        # Best-effort rollback for destinations created in this run.
        if universal.exists():
            shutil.rmtree(universal, ignore_errors=True)
        if manifest["universal_skill"].get("backup"):
            shutil.move(manifest["universal_skill"]["backup"], universal)
        for item in manifest["profiles"].values():
            plugin = Path(item["plugin"])
            config = Path(item["config"])
            if plugin.exists():
                shutil.rmtree(plugin, ignore_errors=True)
            if item.get("plugin_backup"):
                shutil.move(item["plugin_backup"], plugin)
            if item.get("config_backup") and Path(item["config_backup"]).exists():
                shutil.copy2(item["config_backup"], config)
        raise


def remove_managed(path: Path, expected_hash: str, backup: str | None) -> bool:
    if not path.exists() and not path.is_symlink():
        return True
    if sha256(path) != expected_hash:
        print(f"⚠️  conflict preserved: {path}", file=sys.stderr)
        return False
    remove_path(path)
    if backup and Path(backup).exists():
        backup_path_obj = Path(backup)
        if backup_path_obj.is_dir():
            shutil.move(str(backup_path_obj), str(path))
        else:
            shutil.move(str(backup_path_obj), str(path))
    return True


def uninstall() -> None:
    if not MANIFEST.is_file():
        info("no Ginflow installation manifest found; nothing to uninstall")
        return
    manifest = json.loads(MANIFEST.read_text())
    universal = manifest["universal_skill"]
    conflicts = []
    universal_path = Path(universal["path"])
    if universal_path.exists() or universal_path.is_symlink():
        if sha256(universal_path) != universal["installed_hash"]:
            conflicts.append(universal_path)
    for name, item in manifest.get("profiles", {}).items():
        plugin = Path(item["plugin"])
        if (plugin.exists() or plugin.is_symlink()) and sha256(plugin) != item["plugin_hash"]:
            conflicts.append(plugin)
        config = Path(item["config"])
        if config.exists() and sha256(config) != item["config_after_hash"]:
            conflicts.append(config)
    if conflicts:
        for path in conflicts:
            print(f"⚠️  conflict preserved: {path}", file=sys.stderr)
        fail("uninstall blocked by conflicts; no managed paths changed")
    if universal_path.exists() or universal_path.is_symlink():
        remove_managed(universal_path, universal["installed_hash"], universal.get("backup"))
    for name, item in manifest.get("profiles", {}).items():
        remove_managed(Path(item["plugin"]), item["plugin_hash"], item.get("plugin_backup"))
        config = Path(item["config"])
        if item.get("config_backup") and Path(item["config_backup"]).exists():
            shutil.move(item["config_backup"], config)
        ok(f"{name}: Ginflow plugin/config cleaned")
    MANIFEST.unlink()
    ok("Ginflow universal skill and all profile integrations removed")


if len(ARGS) != 1 or ARGS[0] not in {"install", "uninstall"}:
    fail(f"usage: {Path(sys.argv[0]).name} install|uninstall")
if ARGS[0] == "install":
    install()
else:
    uninstall()
PY
