"""Push critical worker blocks to ginflow.notify.target via `hermes send`.

Observer-only kanban_task_blocked hook. Any failure is swallowed so the block
transition is never affected. Fallbacks, guard and repeat handling: later slices.
"""
from __future__ import annotations

import importlib.util
import json
import logging
import os
import re
import subprocess
from pathlib import Path

CRITICAL_KINDS = frozenset({"needs_input", "capability"})
MAX_BODY = 800
logger = logging.getLogger(__name__)

_spec = importlib.util.spec_from_file_location(
    "ginflow_project_config", Path(__file__).resolve().parents[2] / "skills/ginflow/lib/project_config.py"
)
_config = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_config)


def _sanitize(text: object) -> str:
    text = re.sub(r"[\x00-\x1f\x7f]", " ", str(text or ""))
    return re.sub(r"\s+", " ", text).strip()[:MAX_BODY]


def _trace_on(workspace: Path) -> bool:
    flag = os.environ.get("GINFLOW_LOG")
    if flag is not None:
        return flag == "1"
    context = _config.load_config(workspace).get("ginflow")
    return isinstance(context, dict) and context.get("trace") is True


def _load_task(task_id: str, board: str | None) -> dict:
    command = ["hermes", "kanban"] + (["--board", board] if board else []) + ["show", task_id, "--json"]
    result = subprocess.run(command, text=True, capture_output=True, timeout=30)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "unable to read task")
    data = json.loads(result.stdout)
    task = data["task"]
    # `show --json` omits tasks.block_kind; the latest block event carries it.
    if not task.get("block_kind"):
        for event in reversed(data.get("events") or []):
            if event.get("kind") in ("blocked", "dependency_wait"):
                task["block_kind"] = (event.get("payload") or {}).get("kind")
                break
    return task


def build_message(task_id: str, reason: object, profile: object, run_id: object) -> str:
    # ponytail: required_action is the raw reason until #28 parses it.
    reason = _sanitize(reason) or "(no reason given)"
    return _sanitize(
        f"Ginflow block: task {task_id} needs a human. Reason: {reason}. "
        f"Required action: {reason}. Worker: {_sanitize(profile) or 'unknown'}. Run: {run_id}."
    )


def on_task_blocked(task_id: str = "", board: str | None = None, assignee: str | None = None,
                    run_id: int | None = None, reason: str | None = None, **_: object) -> None:
    try:
        task = _load_task(task_id, board)
        workspace = str(task.get("workspace_path") or "")
        if not workspace or task.get("block_kind") not in CRITICAL_KINDS:
            return
        path = Path(workspace)
        if not _trace_on(path):
            return
        error = _config.context_error(path)
        if error:
            logger.warning("ginflow block routing: invalid project config route: %s", error)
            return
        target = _config.configured_notify_target(path)
        if not target:
            return
        message = build_message(task_id, reason, assignee or task.get("assignee"), run_id)
        # Inherits worker HERMES_HOME, so send runs under the worker's profile (B6).
        subprocess.run(["hermes", "send", "--to", target, "-q", message],
                       text=True, capture_output=True, timeout=60)
    except Exception as exc:  # observer-only: never break the block transition
        logger.warning("ginflow block routing failed: %s", exc)


def register(ctx) -> None:
    ctx.register_hook("kanban_task_blocked", on_task_blocked)
