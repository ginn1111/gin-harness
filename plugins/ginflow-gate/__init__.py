"""Blocking Ginflow lifecycle policy for Hermes Kanban tools."""

from __future__ import annotations

import json
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

CORE = Path(__file__).resolve().parents[2] / "skills/ginflow/lib/harness_core.py"
_spec = importlib.util.spec_from_file_location("ginflow_harness_core", CORE)
if not _spec or not _spec.loader:
    raise ImportError(f"unable to load Ginflow harness core: {CORE}")
_core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_core)
artifact_gate = _core.artifact_gate
normalize_card = _core.normalize_card


def _block(message: str) -> dict[str, str]:
    return {"action": "block", "message": f"ginflow-gate: {message}"}


def load_card(task_id: str, board: str | None = None) -> dict:
    command = ["hermes", "kanban"]
    if board:
        command += ["--board", board]
    command += ["show", task_id, "--json"]
    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"unable to read card {task_id}")
    return normalize_card(json.loads(result.stdout))


def validate_completion(card: dict, metadata: dict) -> str | None:
    required = ("id", "title", "objective", "scope", "acceptance", "workspace", "assignee", "links")
    missing = [name for name in required if not card.get(name)]
    if missing:
        return "card missing required fields: " + ", ".join(missing)

    baseline = metadata.get("artifact_baseline")
    verification = metadata.get("verification_result")
    if not isinstance(verification, dict) or not all(verification.get(name) for name in ("commit", "command", "result")):
        return "metadata.verification_result requires non-empty commit, command, and result"
    if not isinstance(baseline, dict):
        return "metadata.artifact_baseline requires commit and exact linked paths"
    if verification["commit"] != baseline.get("commit"):
        return "verification_result.commit must match artifact_baseline.commit"

    workspace = str(card["workspace"])
    if not workspace.startswith("dir:"):
        return f"unsupported workspace for completion validation: {workspace}"
    target = Path(workspace.removeprefix("dir:")).resolve()
    candidate = card | {"artifact_baseline": baseline}
    status = artifact_gate(candidate, target)
    if not status["baseline_complete"]:
        return status["baseline_details"]
    if not status["matches"]:
        return status["drift_details"]
    return None


def pre_tool_call(tool_name: str, args: dict, task_id: str = "", **kwargs):
    if tool_name != "kanban_complete":
        return None
    try:
        selected = str(args.get("task_id") or task_id or os.environ.get("HERMES_KANBAN_TASK") or "").strip()
        if not selected:
            return _block("kanban_complete requires task_id")
        metadata = args.get("metadata")
        if not isinstance(metadata, dict):
            return _block("metadata object is required")
        card = load_card(selected, args.get("board") or os.environ.get("HERMES_KANBAN_BOARD"))
        error = validate_completion(card, metadata)
        return _block(error) if error else None
    except Exception as error:
        return _block(f"validation failed closed: {error}")


def post_tool_call(tool_name: str, result: dict, args: dict, task_id: str = "", **kwargs):
    if tool_name != "kanban_complete":
        return None
    if not result.get("success"):
        return None
    try:
        selected = str(args.get("task_id") or task_id or os.environ.get("HERMES_KANBAN_TASK") or "").strip()
        if not selected:
            return None
        card = load_card(selected, args.get("board") or os.environ.get("HERMES_KANBAN_BOARD"))
        workspace = str(card.get("workspace", ""))
        if not workspace.startswith("dir:"):
            return None
        target = Path(workspace.removeprefix("dir:")).resolve()
        if not target.is_dir():
            return None

        links = card.get("links", [])
        if not isinstance(links, list) or not links:
            return None

        updated = []
        for link in links:
            path_str = link if isinstance(link, str) else link.get("path") if isinstance(link, dict) else None
            if not isinstance(path_str, str) or "://" in path_str:
                continue
            artifact = (target / path_str).resolve()
            try:
                artifact.relative_to(target)
            except ValueError:
                continue
            if not artifact.is_file():
                continue

            content = artifact.read_text()
            footer = f"\n\n---\n**Status: completed** — linked card {card.get('id')} is done.\n"
            if not content.endswith(footer.rstrip()):
                artifact.write_text(content.rstrip() + footer + "\n")
                updated.append(path_str)

        if updated:
            print(f"ginflow-gate: marked linked artifacts done: {', '.join(updated)}", file=sys.stderr)
    except Exception as error:
        print(f"ginflow-gate: artifact update warning: {error}", file=sys.stderr)
    return None


def register(ctx):
    ctx.register_hook("pre_tool_call", pre_tool_call)
    ctx.register_hook("post_tool_call", post_tool_call)
