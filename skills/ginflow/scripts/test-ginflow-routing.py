#!/usr/bin/env python3
"""Test ginflow-routing plugin activation based on ginflow skill presence."""

import importlib.util
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PLUGIN = ROOT / "plugins/ginflow-routing/__init__.py"

spec = importlib.util.spec_from_file_location("ginflow_routing", PLUGIN)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

_ginflow_loaded = module._ginflow_loaded
_routing_context = module._routing_context


def test_no_ginflow_skill():
    """Routing is no-op when ginflow skill absent."""
    with tempfile.TemporaryDirectory(prefix="ginrouting-test-") as tmp:
        hermes_home = Path(tmp)
        profile = "testprofile"

        old_home = os.environ.get("HERMES_HOME")
        old_profile = os.environ.get("HERMES_PROFILE")
        os.environ["HERMES_HOME"] = str(hermes_home)
        os.environ["HERMES_PROFILE"] = profile
        try:
            assert _ginflow_loaded() is False, \
                "_ginflow_loaded() should be False with no ginflow SKILL.md"
            result = _routing_context()
            assert result is None, \
                "_routing_context() should return None when ginflow not loaded"
        finally:
            if old_home:
                os.environ["HERMES_HOME"] = old_home
            else:
                os.environ.pop("HERMES_HOME", None)
            if old_profile:
                os.environ["HERMES_PROFILE"] = old_profile
            else:
                os.environ.pop("HERMES_PROFILE", None)

    print("PASS: no ginflow → routing not called")


def test_ginflow_skill_active():
    """Routing injects context when ginflow skill present."""
    with tempfile.TemporaryDirectory(prefix="ginrouting-test-") as tmp:
        hermes_home = Path(tmp)
        profile = "testprofile"

        skill_dir = hermes_home / "profiles" / profile / "skills" / "ginflow"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: ginflow\n---\n# ginflow\n"
        )

        old_home = os.environ.get("HERMES_HOME")
        old_profile = os.environ.get("HERMES_PROFILE")
        os.environ["HERMES_HOME"] = str(hermes_home)
        os.environ["HERMES_PROFILE"] = profile
        try:
            assert _ginflow_loaded() is True, \
                "_ginflow_loaded() should be True with ginflow SKILL.md"

            result = _routing_context()
            assert result is not None, \
                "_routing_context() should return dict when ginflow loaded"
            assert "context" in result, \
                "result should have 'context' key"
            assert "ginflow-routing" in result["context"], \
                "context should contain plugin marker '[ginflow-routing:'"
            assert "shaping" in result["context"] or "resume" in result["context"], \
                "context should route to shaping or resume"
        finally:
            if old_home:
                os.environ["HERMES_HOME"] = old_home
            else:
                os.environ.pop("HERMES_HOME", None)
            if old_profile:
                os.environ["HERMES_PROFILE"] = old_profile
            else:
                os.environ.pop("HERMES_PROFILE", None)

    print("PASS: ginflow active → routing called")


if __name__ == "__main__":
    test_no_ginflow_skill()
    test_ginflow_skill_active()
    print("ginflow routing test passed")
