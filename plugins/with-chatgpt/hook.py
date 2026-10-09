"""Fast, local-only optional context injection."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

from .state import session_enabled

_MAX_CONTEXT = 2048
_SAFE_PHASES = {"INIT", "PLAN_RECEIVED", "EXECUTING", "EXECUTED_LOCAL", "EXECUTED_SENT", "DONE", "BLOCKED"}
_SENSITIVE_TEXT = ("token", "secret", "password", "cookie", "credential", "bearer", "refresh", "admin", "pairing")


def _safe_text(value: object, limit: int) -> str:
    if not isinstance(value, str):
        return ""
    normalized = " ".join(value.split())[:limit]
    lowered = normalized.lower()
    if any(marker in lowered for marker in _SENSITIVE_TEXT):
        return ""
    return normalized


def _workspace_root(payload: dict[str, Any]) -> Path | None:
    for key in ("workspace", "workspace_root", "cwd"):
        value = payload.get(key)
        if isinstance(value, str) and value and "\x00" not in value:
            return Path(value).expanduser()
    return None


def _local_checkpoint(root: Path | None) -> dict[str, Any]:
    if root is None:
        return {}
    # The hook never probes a bridge or starts a process. Checkpoint is optional.
    configured = _state_dir()
    if configured is None:
        return {}
    try:
        workspace_id = _safe_text(payload_workspace_id(root), 100)
        if not workspace_id:
            return {}
        file = configured / "sessions" / f"{workspace_id}.json"
        raw = json.loads(file.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except (OSError, ValueError):
        return {}


def _state_dir() -> Path | None:
    value = os.environ.get("C2C_STATE_DIR", "").strip()
    if value:
        return Path(value).expanduser()
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "codex-with-chatgpt"
    if sys.platform == "win32":
        return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "codex-with-chatgpt"
    return Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state")) / "codex-with-chatgpt"


def payload_workspace_id(root: Path) -> str:
    """Match C2C Workspace.id without importing or running its Node runtime."""
    try:
        real_root = root.resolve(strict=True)
        if not real_root.is_dir():
            return ""
        normalized = str(real_root)
        if sys.platform in {"darwin", "win32"}:
            normalized = normalized.lower()
        return hashlib.sha256(normalized.encode()).hexdigest()[:12]
    except (OSError, RuntimeError, ValueError):
        return ""


def pre_llm_call(*, session_id: str = "", state: Any = None, **payload: Any) -> dict[str, str] | None:
    try:
        if state is None or not session_enabled(state, session_id):
            return None
        root = _workspace_root(payload)
        checkpoint = _local_checkpoint(root)
        saved = checkpoint.get("checkpoint") if isinstance(checkpoint, dict) else None
        if not isinstance(saved, dict):
            saved = {}
        phase = _safe_text(saved.get("protocolState"), 40)
        if phase not in _SAFE_PHASES:
            phase = "INIT"
        next_step = _safe_text(saved.get("nextExpectedStep"), 240) or {
            "INIT": "Use the C2C skill to establish or resume the explicit planning workflow.",
            "PLAN_RECEIVED": "Execute the approved plan locally; do not ask ChatGPT to edit files.",
            "EXECUTING": "Continue Hermes execution and record a bounded result.",
            "EXECUTED_LOCAL": "Send the execution checkpoint for ChatGPT review through the explicit browser workflow.",
            "EXECUTED_SENT": "Wait for explicit ChatGPT review; do not start browser work in this hook.",
            "DONE": "No action; preserve completed checkpoint.",
            "BLOCKED": "Run the explicit doctor/setup recovery command before continuing.",
        }.get(phase, "Run the explicit C2C status/doctor workflow.")
        context = (
            "Hermes with ChatGPT collaboration is enabled for this session. "
            f"C2C phase: {phase}. "
            "ChatGPT plans/reviews; Hermes executes; C2C observation is read-only. "
            f"Next: {next_step} Recovery: c2c status --json or c2c doctor --json."
        )
        return {"context": context[:_MAX_CONTEXT]}
    except Exception:
        return None
