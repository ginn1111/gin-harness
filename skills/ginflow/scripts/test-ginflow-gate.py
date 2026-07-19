#!/usr/bin/env python3
import importlib.util
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PLUGIN = ROOT / "plugins/ginflow-gate/__init__.py"

spec = importlib.util.spec_from_file_location("ginflow_gate", PLUGIN)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

card = {
    "id": "GATE-1",
    "title": "Gate",
    "objective": "Enforce completion",
    "scope": ["plugin"],
    "acceptance": ["bad completion rejected"],
    "workspace": "dir:/tmp/target",
    "status": "running",
    "assignee": "worker",
    "links": ["docs/briefs/GATE-1.md"],
}
setattr(module, "load_card", lambda task_id, board=None: card)

blocked = module.pre_tool_call("kanban_complete", {"task_id": "GATE-1", "metadata": {}}, "", profile="worker")
assert blocked["action"] == "block"
assert "verification_result" in blocked["message"]

setattr(module, "validate_completion", lambda card, metadata: None)
allowed = module.pre_tool_call(
    "kanban_complete",
    {
        "task_id": "GATE-1",
        "metadata": {
            "verification_result": {"commit": "abc", "command": "make test", "result": "passed"},
            "artifact_baseline": {"commit": "abc", "paths": ["docs/briefs/GATE-1.md"]},
        },
    },
    "",
    profile="worker",
)
assert allowed is None

setattr(module, "validate_completion", lambda card, metadata: "linked artifact drift: docs/briefs/GATE-1.md")
blocked = module.pre_tool_call(
    "kanban_complete",
    {
        "task_id": "GATE-1",
        "metadata": {
            "verification_result": {"commit": "abc", "command": "make test", "result": "passed"},
            "artifact_baseline": {"commit": "abc", "paths": ["docs/briefs/GATE-1.md"]},
        },
    },
    "",
)
assert blocked["action"] == "block"
assert "drift" in blocked["message"]

setattr(module, "load_card", lambda task_id, board=None: (_ for _ in ()).throw(RuntimeError("DB unavailable")))
failed_closed = module.pre_tool_call("kanban_complete", {"task_id": "GATE-1", "metadata": {}}, "")
assert failed_closed["action"] == "block"
assert "validation failed closed" in failed_closed["message"]

print("ginflow gate rejection test passed")
