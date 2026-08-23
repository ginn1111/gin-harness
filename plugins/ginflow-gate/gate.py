"""Blocking Ginflow lifecycle policy for Hermes Kanban tools."""

from __future__ import annotations

import json
import importlib.util
import os
import subprocess
from pathlib import Path

CORE = Path(__file__).resolve().parents[2] / "core/ginflow-core/harness_core.py"
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


def linked_documents_missing_completion(card: dict, target: Path) -> list[str]:
    """Return local linked spec/plan paths without completion footer."""
    missing = []
    for link in card.get("links", []):
        path_str = link if isinstance(link, str) else link.get("path") if isinstance(link, dict) else None
        if not isinstance(path_str, str) or "://" in path_str:
            continue
        artifact = (target / path_str).resolve()
        try:
            artifact.relative_to(target)
        except ValueError:
            continue
        relative = artifact.relative_to(target)
        if artifact.is_file() and artifact.suffix.lower() == ".md" and any(
            part in {"specs", "plans"} for part in relative.parts
        ) and "**Status: completed**" not in artifact.read_text(encoding="utf-8"):
            missing.append(path_str)
    return sorted(missing)


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

    incomplete = linked_documents_missing_completion(card, target)
    if incomplete:
        return (
            "linked target-local documents are not marked completed: " + ", ".join(incomplete)
            + ". Finalize each document with '**Status: completed**', commit those changes, "
              "update verification_result.commit and artifact_baseline.commit, then retry kanban_complete."
        )

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
    """Retained compatibility hook; linked documents are finalized before completion."""
    return None


def register(ctx):
    ctx.register_hook("pre_tool_call", pre_tool_call)
    ctx.register_hook("post_tool_call", post_tool_call)
