#!/usr/bin/env python3
"""Register the shared skill directory in target profile config.yaml files.

Dry-run by default. Requires PyYAML only when --apply is used.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys

PROFILES = ("ginb", "ginr", "gins", "gino")
EXTERNAL_DIR = "~/.hermes/shared-skills/mattpocock-skills/skills"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    for profile in PROFILES:
        path = Path.home() / ".hermes" / "profiles" / profile / "config.yaml"
        if not args.apply:
            print(f"[dry-run] merge skills.external_dirs += {EXTERNAL_DIR} into {path}")
            continue
        try:
            import yaml
        except ImportError:
            print("PyYAML is required: python -m pip install -r requirements.txt", file=sys.stderr)
            return 1
        data = {}
        if path.exists() and path.read_text().strip():
            loaded = yaml.safe_load(path.read_text())
            if loaded is not None and not isinstance(loaded, dict):
                raise ValueError(f"Expected mapping in {path}")
            data = loaded or {}
        skills = data.setdefault("skills", {})
        if not isinstance(skills, dict):
            raise ValueError(f"Expected skills mapping in {path}")
        dirs = skills.setdefault("external_dirs", [])
        if not isinstance(dirs, list):
            raise ValueError(f"Expected skills.external_dirs list in {path}")
        if EXTERNAL_DIR not in dirs:
            dirs.append(EXTERNAL_DIR)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(data, sort_keys=False))
        print(f"✅ Shared skills registered — {profile}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
