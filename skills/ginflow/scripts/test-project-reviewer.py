#!/usr/bin/env python3
"""Project reviewer config: validate against profiles, seed Hermes default, fail closed."""
import importlib.util
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("pc", ROOT / "skills/ginflow/lib/project_config.py")
pc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pc)

PROFILES = ["default", "ginb", "gintary"]


def project(extra=""):
    d = Path(tempfile.mkdtemp(prefix="ginflow-reviewer-")).resolve()
    (d / ".ginflow.yaml").write_text(
        f"version: 1\nginflow:\n  board: b\n  workspace: {d}\n{extra}"
    )
    return d


def seed(target, current=None):
    return pc.seed_default_reviewer(
        target, installed_profiles=PROFILES, current=current, write=lambda _: None
    )


def main():
    # valid reviewer seeds Hermes default
    t = project("  reviewer:\n    profile: gintary\n")
    assert pc.reviewer_error(t, PROFILES) is None
    assert pc.configured_reviewer(t) == "gintary"
    assert seed(t) == ("gintary", ["gintary"])
    # already equal: no rewrite
    assert seed(t, current="gintary") == ("gintary", [])
    # absent reviewer: existing Hermes config untouched
    t = project()
    assert pc.reviewer_error(t, PROFILES) is None
    assert seed(t, current="gintary") == (None, [])
    # invalid / unknown fail closed, nothing written
    for extra, needle in [
        ("  reviewer:\n    profile: nobody\n", "not an installed"),
        ("  reviewer: gintary\n", "must be a mapping"),
        ("  reviewer:\n    profile: ''\n", "non-empty"),
        ("  reviewer:\n    profile: gintary\n    x: 1\n", "unknown"),
    ]:
        t = project(extra)
        assert needle in pc.reviewer_error(t, PROFILES), extra
        writes = []
        try:
            pc.seed_default_reviewer(t, installed_profiles=PROFILES, current=None, write=writes.append)
        except pc.ReviewerConfigError:
            assert not writes
        else:
            raise AssertionError(f"no failure for {extra}")
    print("PASS: project reviewer config")


if __name__ == "__main__":
    main()
