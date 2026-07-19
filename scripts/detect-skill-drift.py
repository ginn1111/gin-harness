#!/usr/bin/env python3
"""Reject profile-local skills that shadow setup-repo skills."""

import argparse
from pathlib import Path

import yaml


def skill_paths(root: Path) -> dict[str, Path]:
    skills = {}
    if not root.is_dir():
        return skills
    for manifest in root.rglob("SKILL.md"):
        text = manifest.read_text()
        if not text.startswith("---\n"):
            continue
        data = yaml.safe_load(text.split("---\n", 2)[1]) or {}
        if name := data.get("name"):
            skills[name] = manifest.parent.resolve()
    return skills


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--profiles-dir", required=True, type=Path)
    parser.add_argument("profiles", nargs="+")
    args = parser.parse_args()

    canonical = {}
    for root in (
        args.repo / "skills",
        args.repo / "community/mattpocock-skills/skills",
        args.repo / ".hermes/shared-skills/mattpocock-skills/skills",
    ):
        canonical.update(skill_paths(root))

    drift = []
    for profile in args.profiles:
        local = skill_paths(args.profiles_dir / profile / "skills")
        for name in sorted(canonical.keys() & local.keys()):
            if local[name] != canonical[name]:
                drift.append((profile, name, local[name], canonical[name]))

    for profile, name, local, expected in drift:
        print(f"{profile}: local skill '{name}' shadows repo skill")
        print(f"  local: {local}")
        print(f"  repo:  {expected}")
    return bool(drift)


if __name__ == "__main__":
    raise SystemExit(main())
