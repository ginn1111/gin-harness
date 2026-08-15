#!/usr/bin/env python3
"""Test ginflow-routing plugin activation based on current session skill state."""

import importlib.util
import json
import os
import subprocess
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
_route = module._route


def test_workspace_and_status_routes():
    workspace = str(Path.cwd().resolve())
    assert _route([{"id": "other", "workspace_path": "/tmp/other", "status": "in_progress"}])["route"] == "no_card"
    assert _route([
        {"id": "one", "workspace_path": workspace, "status": "next"},
        {"id": "two", "workspace_path": workspace, "status": "in_progress"},
    ])["route"] == "needs_card_selection"
    assert _route([{"id": "blocked", "workspace_path": workspace, "status": "blocked"}])["route"] == "blocked_card"
    assert _route([{"id": "next", "workspace_path": "dir:" + workspace, "status": "next"}])["route"] == "validate_card_docs"
    assert _route([{"id": "ready", "workspace_path": workspace, "status": "in_progress"}])["route"] == "ready_to_start"
    assert _route([{"id": "running", "workspace_path": workspace, "status": "running"}])["route"] == "ready_to_start"
    assert _route([{"id": "todo", "workspace_path": workspace, "status": "todo"}])["route"] == "validate_card_docs"
    assert _route([{"id": "ready-state", "workspace_path": workspace, "status": "ready"}])["route"] == "validate_card_docs"
    assert _route([{"id": "other", "workspace_path": "/tmp/other", "status": "in_progress"}], "other")["route"] == "workspace_mismatch"
    print("PASS: workspace/status routes")



def test_no_ginflow_skill():
    """Routing is no-op when ginflow skill absent from session."""
    old_skills = os.environ.get("HERMES_TUI_SKILLS")
    os.environ["HERMES_TUI_SKILLS"] = ""
    try:
        assert _ginflow_loaded() is False, \
            "_ginflow_loaded() should be False with no active ginflow session skill"
        result = _routing_context()
        assert result is None, \
            "_routing_context() should return None when ginflow not loaded"
    finally:
        if old_skills is not None:
            os.environ["HERMES_TUI_SKILLS"] = old_skills
        else:
            os.environ.pop("HERMES_TUI_SKILLS", None)

    print("PASS: no ginflow → routing not called")


def test_ginflow_skill_active():
    """Routing injects context when ginflow skill active in session."""
    old_skills = os.environ.get("HERMES_TUI_SKILLS")
    old_task = os.environ.pop("HERMES_KANBAN_TASK", None)
    os.environ["HERMES_TUI_SKILLS"] = "other, ginflow, plan"
    try:
        assert _ginflow_loaded() is True, \
            "_ginflow_loaded() should be True with active ginflow session skill"

        result = _routing_context()
        assert result is not None, \
            "_routing_context() should return dict when ginflow loaded"
        assert "context" in result, \
            "result should have 'context' key"
        assert "ginflow-routing" in result["context"], \
            "context should contain plugin marker '[ginflow-routing:'"
        assert "route=" in result["context"] and "mutation_allowed=" in result["context"], \
            "context should expose structured deterministic route"
        assert any(marker in result["context"] for marker in (
            "Report", "Validate", "Resume", "Do not implement",
        )), "context should provide route action"
    finally:
        if old_skills is not None:
            os.environ["HERMES_TUI_SKILLS"] = old_skills
        else:
            os.environ.pop("HERMES_TUI_SKILLS", None)
        if old_task is not None:
            os.environ["HERMES_KANBAN_TASK"] = old_task

    print("PASS: ginflow active → routing called")


def test_live_tmp_project_card():
    """Create a real temporary Kanban card and route it from its workspace."""
    body = (
        "Objective: Route temporary card\n"
        "Scope:\n- routing\n"
        "Acceptance:\n- route blocked card\n"
        "Links:\n- docs/briefs/TMP-1.md"
    )
    with tempfile.TemporaryDirectory(prefix="ginflow-routing-project-") as project, tempfile.TemporaryDirectory(prefix="ginflow-routing-home-") as home:
        target = Path(project)
        (target / "docs/briefs").mkdir(parents=True)
        (target / "docs/briefs/TMP-1.md").write_text("# Temporary brief\n")
        env = os.environ | {"HERMES_HOME": home, "HERMES_TUI_SKILLS": "ginflow"}
        subprocess.run(["hermes", "kanban", "init"], env=env, check=True, capture_output=True, text=True)
        created = subprocess.run(
            ["hermes", "kanban", "create", "TMP-1 — temporary routing card", "--body", body,
             "--assignee", "ginb", "--workspace", f"dir:{target}",
             "--initial-status", "blocked", "--json"],
            env=env, check=True, capture_output=True, text=True,
        )
        task = json.loads(created.stdout)
        task_id = task["id"]
        old_cwd = Path.cwd()
        try:
            os.chdir(target)
            result = _route([task], task_id)
            assert result["route"] == "blocked_card", result
            assert result["action"] == "orchestrator"
        finally:
            os.chdir(old_cwd)
    print("PASS: live temporary project/card routing")


def test_live_tmp_next_card_docs():
    """Route a real temporary card through startup document validation."""
    body = (
        "Objective: Start temporary card\n"
        "Scope:\n- routing\n"
        "Acceptance:\n- validate docs\n"
        "Links:\n- docs/briefs/TMP-2.md"
    )
    with tempfile.TemporaryDirectory(prefix="ginflow-routing-project-") as project, tempfile.TemporaryDirectory(prefix="ginflow-routing-home-") as home:
        target = Path(project)
        (target / "docs/briefs").mkdir(parents=True)
        (target / "docs/briefs/TMP-2.md").write_text("# Temporary brief\n")
        env = os.environ | {"HERMES_HOME": home}
        subprocess.run(["hermes", "kanban", "init"], env=env, check=True, capture_output=True, text=True)
        created = subprocess.run(
            ["hermes", "kanban", "create", "TMP-2 — temporary startup card", "--body", body,
             "--assignee", "ginb", "--workspace", f"dir:{target}",
             "--initial-status", "blocked", "--json"],
            env=env, check=True, capture_output=True, text=True,
        )
        task = json.loads(created.stdout)
        task["status"] = "next"
        task["body"] = body
        old_cwd = Path.cwd()
        old_loader = module._load_tasks
        try:
            os.chdir(target)
            module._load_tasks = lambda: [task]
            os.environ["HERMES_TUI_SKILLS"] = "ginflow"
            os.environ["HERMES_KANBAN_TASK"] = task["id"]
            result = _routing_context()
            assert result and "route=ready_to_start" in result["context"], result
            assert "mutation_allowed=False" in result["context"], result
        finally:
            module._load_tasks = old_loader
            os.chdir(old_cwd)
            os.environ.pop("HERMES_TUI_SKILLS", None)
            os.environ.pop("HERMES_KANBAN_TASK", None)
    print("PASS: live temporary next-card doc validation")


if __name__ == "__main__":
    test_workspace_and_status_routes()
    test_no_ginflow_skill()
    test_ginflow_skill_active()
    test_live_tmp_project_card()
    test_live_tmp_next_card_docs()
    print("ginflow routing test passed")
