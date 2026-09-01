#!/usr/bin/env python3
"""Integration test for gate approval plus native Kanban review mutation."""

import importlib.util
import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BOARD = "gin-harness-review-testing"
BODY = (
    "Objective: Native review transition\n"
    "Scope:\n- transition\n"
    "Acceptance:\n- running becomes review\n"
    "Links:\n- docs/specs/HARNESS-REVIEW-1.md"
)
SPEC = "---\nstatus: completed\n---\n# Review transition\n"


def load_gate():
    path = ROOT / "plugins/ginflow-gate/gate.py"
    spec = importlib.util.spec_from_file_location("native_review_gate", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_hermes(env, *args):
    return subprocess.run(
        ["hermes", *args], env=env, text=True, capture_output=True, check=True
    )


def test_native_review_transition():
    with tempfile.TemporaryDirectory(prefix="ginflow-review-project-") as project, tempfile.TemporaryDirectory(prefix="ginflow-review-home-") as home:
        target = Path(project)
        (target / "docs/specs").mkdir(parents=True)
        (target / "docs/specs/HARNESS-REVIEW-1.md").write_text(SPEC)
        subprocess.run(["git", "init", "-q"], cwd=target, check=True)
        subprocess.run(["git", "config", "user.name", "Ginflow Test"], cwd=target, check=True)
        subprocess.run(["git", "config", "user.email", "ginflow@example.test"], cwd=target, check=True)
        subprocess.run(["git", "add", "."], cwd=target, check=True)
        subprocess.run(["git", "commit", "-qm", "baseline"], cwd=target, check=True)
        baseline = subprocess.run(["git", "rev-parse", "HEAD"], cwd=target, text=True, capture_output=True, check=True).stdout.strip()
        env = os.environ | {"HERMES_HOME": home, "HERMES_KANBAN_BOARD": BOARD}
        run_hermes(env, "kanban", "init")
        run_hermes(env, "kanban", "boards", "create", BOARD)
        created = run_hermes(env, "kanban", "--board", BOARD, "create", "HARNESS-REVIEW-1 — transition", "--body", BODY, "--assignee", "ginb", "--workspace", f"dir:{target}", "--initial-status", "blocked", "--json")
        task_id = json.loads(created.stdout)["id"]
        run_hermes(env, "kanban", "--board", BOARD, "unblock", task_id)
        run_hermes(env, "kanban", "--board", BOARD, "claim", task_id)
        old_home = os.environ.get("HERMES_HOME")
        old_board = os.environ.get("HERMES_KANBAN_BOARD")
        os.environ["HERMES_HOME"] = home
        os.environ["HERMES_KANBAN_BOARD"] = BOARD
        metadata = {"verification_result": {"commit": baseline, "command": "make test", "result": "passed"}, "artifact_baseline": {"commit": baseline, "paths": ["docs/specs/HARNESS-REVIEW-1.md"]}}
        gate = load_gate()
        card = gate.load_card(task_id, board=BOARD)
        assert gate.pre_tool_call("kanban_request_review", {"task_id": task_id, "metadata": metadata}, "", board=BOARD) is None
        run_hermes(env, "kanban", "--board", BOARD, "request-review", task_id, "--summary", "transition verified", "--metadata", json.dumps(metadata), "--force")
        reviewed = json.loads(run_hermes(env, "kanban", "--board", BOARD, "show", task_id, "--json").stdout)["task"]
        assert reviewed["status"] == "review"
        show = json.loads(run_hermes(env, "kanban", "--board", BOARD, "show", task_id, "--json").stdout)
        assert show["task"]["status"] == "review"
        review_runs = [run for run in show.get("runs", []) if run.get("summary") == "transition verified"]
        assert review_runs, show
        assert review_runs[0]["metadata"]["verification_result"]["command"] == "make test"

        rejected = run_hermes(env, "kanban", "--board", BOARD, "create", "HARNESS-REVIEW-1-rejected", "--body", BODY, "--assignee", "ginb", "--workspace", f"dir:{target}", "--initial-status", "blocked", "--json")
        rejected_id = json.loads(rejected.stdout)["id"]
        run_hermes(env, "kanban", "--board", BOARD, "unblock", rejected_id)
        run_hermes(env, "kanban", "--board", BOARD, "claim", rejected_id)
        blocked = gate.pre_tool_call("kanban_request_review", {"task_id": rejected_id, "metadata": {}}, "", board=BOARD)
        assert blocked["action"] == "block"
        rejected_card = json.loads(run_hermes(env, "kanban", "--board", BOARD, "show", rejected_id, "--json").stdout)["task"]
        assert rejected_card["status"] == "running", rejected_card


if __name__ == "__main__":
    test_native_review_transition()
    print("PASS: native running -> review transition")
