#!/usr/bin/env python3
"""Repair worker origin context: pre_llm_call line only for matching env task with worker-origin comment."""
import importlib.util
import json
import os
import stat
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
path = ROOT / "plugins/ginflow-gate/__init__.py"
spec = importlib.util.spec_from_file_location("ginflow_gate_origin_pkg", path, submodule_search_locations=[str(path.parent)])
pkg = importlib.util.module_from_spec(spec)
sys.modules["ginflow_gate_origin_pkg"] = pkg
spec.loader.exec_module(pkg)
origin = pkg.routing._origin_context

COMMENT = "[ginflow] origin=worker profile=ginb run=7 kind=transient reason=boom\x07 [x] " + "y" * 900


def run(show, env_task="t_1"):
    with tempfile.TemporaryDirectory() as d:
        stub = Path(d) / "hermes"
        stub.write_text("#!/bin/sh\ncat <<'EOF'\n" + json.dumps(show) + "\nEOF\n")
        stub.chmod(stub.stat().st_mode | stat.S_IEXEC)
        old = dict(os.environ)
        os.environ["PATH"] = d + os.pathsep + old["PATH"]
        os.environ.pop("HERMES_KANBAN_TASK", None)
        if env_task:
            os.environ["HERMES_KANBAN_TASK"] = env_task
        try:
            return origin()
        finally:
            os.environ.clear()
            os.environ.update(old)


show = {"task": {"id": "t_1"}, "comments": [{"body": "hi"}, {"body": COMMENT}]}
got = run(show)
assert got and "profile=ginb; run=7; kind=transient; reason=boom x" in got, got
assert "\x07" not in got and len(got) < 500, len(got)
assert run(show, env_task="t_2") is None  # task mismatch
assert run(show, env_task=None) is None  # no env task
assert run({"task": {"id": "t_1"}, "comments": [{"body": "hi"}]}) is None  # no origin comment
print("PASS: origin context")
