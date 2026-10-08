#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 - "$ROOT" "$@" <<'PY'
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(sys.argv[1]).resolve()
ARGS = sys.argv[2:]
MANIFEST = Path(os.environ.get("GINFLOW_INSTALL_MANIFEST", str(ROOT / ".ginflow-install.json"))).expanduser().resolve()
VERSION = 1



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


def write_manifest(manifest: dict[str, Any]) -> None:
    temporary = MANIFEST.with_name(MANIFEST.name + ".tmp")
    temporary.write_text(json.dumps(manifest, indent=2) + "\n")
    os.replace(temporary, MANIFEST)


def install(profile_names: list[str]) -> None:
    if MANIFEST.exists():
        info("existing Ginflow installation found; cleaning it before reinstall")
        uninstall()
    source_skill = ROOT / "skills/ginflow"
    if not source_skill.is_dir():
        fail("setup-repo skill source directory is missing")

    real_home = Path(os.environ.get("HERMES_REAL_HOME", str(Path.home()))).expanduser().resolve()
    profiles_dir = Path(os.environ.get("HERMES_PROFILES_DIR", str(real_home / ".hermes/profiles"))).expanduser().resolve()
    destinations = {name: profiles_dir / name / "skills/ginflow" for name in profile_names}
    for name, destination in destinations.items():
        if not (profiles_dir / name / "config.yaml").is_file():
            fail(f"Hermes profile missing or invalid: {name}")
        if destination.exists() and not destination.is_dir():
            fail(f"managed destination is not a directory: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if backup_path(destination).exists():
            fail(f"backup already exists; resolve before install: {backup_path(destination)}")

    manifest: dict[str, Any] = {"version": VERSION, "source_root": str(ROOT), "profiles": {}}
    try:
        for name, destination in destinations.items():
            backup = backup_existing(destination)
            if destination.exists() or destination.is_symlink():
                remove_path(destination)
            copy_tree(source_skill, destination)
            manifest["profiles"][name] = {
                "skill": str(destination),
                "skill_hash": sha256(destination),
                "skill_backup": backup,
            }
            ok(f"{name}: Ginflow skill installed at {destination}")
        write_manifest(manifest)
        ok(f"manifest written to {MANIFEST}")
    except Exception:
        print("❌ installation failed; restoring destinations", file=sys.stderr)
        for item in manifest["profiles"].values():
            destination = Path(item["skill"])
            remove_path(destination)
            if item.get("skill_backup"):
                shutil.move(item["skill_backup"], destination)
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
    conflicts = []
    for item in manifest.get("profiles", {}).values():
        skill = Path(item["skill"])
        if (skill.exists() or skill.is_symlink()) and sha256(skill) != item["skill_hash"]:
            conflicts.append(skill)

    if conflicts:
        for path in conflicts:
            print(f"⚠️  conflict preserved: {path}", file=sys.stderr)
        fail("uninstall blocked by conflicts; no managed paths changed")
    for name, item in manifest.get("profiles", {}).items():
        remove_managed(Path(item["skill"]), item["skill_hash"], item.get("skill_backup"))
        ok(f"{name}: Ginflow skill removed")
    MANIFEST.unlink()


if not ARGS or ARGS[0] not in {"install", "uninstall"}:
    fail(f"usage: {Path(sys.argv[0]).name} install <profile> [profile ...]|uninstall")
if ARGS[0] == "install":
    if len(ARGS) < 2:
        fail("install requires at least one Hermes profile")
    install(ARGS[1:])
elif len(ARGS) == 1:
    uninstall()
else:
    fail("uninstall accepts no profile arguments")
PY
