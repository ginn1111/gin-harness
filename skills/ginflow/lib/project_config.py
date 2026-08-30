"""Project-local canonical Ginflow Kanban context."""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Any, Mapping

try:
    import yaml
except ImportError:  # pragma: no cover - the setup requires PyYAML
    yaml = None

CONFIG_RELATIVE_PATH = Path(".ginflow.yaml")
CONFIG_VERSION = 1


class ContextInitializationError(ValueError):
    """Raised when first-use context cannot be resolved safely."""


def config_path(workspace: Path) -> Path:
    return Path(workspace).expanduser().resolve() / CONFIG_RELATIVE_PATH


def config_exists(workspace: Path) -> bool:
    """Return whether the project-local context file exists."""
    return config_path(workspace).is_file()


def load_config(workspace: Path) -> dict[str, Any]:
    path = config_path(workspace)
    if not path.is_file() or yaml is None:
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return {}
    return data if isinstance(data, dict) else {}


def context_error(workspace: Path) -> str | None:
    """Validate an existing project config without silently repairing it."""
    path = config_path(workspace)
    if not path.exists():
        return None
    if yaml is None:
        return "project config requires PyYAML"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return f"project config is malformed: {exc}"
    if not isinstance(data, dict) or data.get("version") != CONFIG_VERSION:
        return f"project config must declare version: {CONFIG_VERSION}"
    context = data.get("ginflow")
    if not isinstance(context, dict):
        return "project config is missing the ginflow mapping"
    board = context.get("board")
    configured = context.get("workspace")
    if not isinstance(board, str) or not board.strip():
        return "project config is missing ginflow.board"
    if not isinstance(configured, str) or not configured.strip():
        return "project config is missing ginflow.workspace"
    try:
        expected = Path(configured).expanduser().resolve()
    except (OSError, TypeError, ValueError):
        return "project config has an invalid workspace"
    actual = Path(workspace).expanduser().resolve()
    if expected != actual:
        return f"project config workspace {expected} does not match {actual}"
    return None


def configured_context(workspace: Path) -> dict[str, str]:
    data = load_config(workspace)
    context = data.get("ginflow", data)
    if not isinstance(context, dict):
        return {}
    result = {}
    for key in ("board", "workspace"):
        value = context.get(key)
        if isinstance(value, str) and value.strip():
            result[key] = value.strip()
    return result


def context_mismatch(workspace: Path) -> str | None:
    """Return a deterministic error when a config belongs to another project."""
    error = context_error(workspace)
    return error if error and "workspace" in error else None


def active_board(env: Mapping[str, str] | None = None) -> str | None:
    values = env if env is not None else os.environ
    explicit = values.get("HERMES_KANBAN_BOARD", "").strip()
    if explicit:
        return explicit
    try:
        result = subprocess.run(
            ["hermes", "kanban", "boards", "current"],
            text=True, capture_output=True, timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    for line in result.stdout.splitlines():
        match = re.match(r"^\s*Current board:\s*(\S+)\s*$", line)
        if match:
            return match.group(1)
    return None


def resolve_board(workspace: Path, explicit: str | None = None, env: Mapping[str, str] | None = None) -> str | None:
    """Resolve explicit override, environment override, then project config, then active board."""
    if context_error(workspace):
        return None
    if explicit and explicit.strip():
        return explicit.strip()
    values = env if env is not None else os.environ
    if values.get("HERMES_KANBAN_BOARD", "").strip():
        return values["HERMES_KANBAN_BOARD"].strip()
    return configured_context(workspace).get("board") or active_board(values)


def persist_context(workspace: Path, *, board: str | None) -> Path | None:
    """Persist only complete, resolved context; never create a partial config."""
    workspace = Path(workspace).expanduser().resolve()
    if not board or not workspace.is_dir() or yaml is None:
        return None
    path = config_path(workspace)
    if path.exists():
        return None
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"version": CONFIG_VERSION, "ginflow": {"board": board, "workspace": str(workspace)}}
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    os.replace(temporary, path)
    return path


def initialize_context(
    workspace: Path,
    *,
    choice: str,
    current_board: str | None,
    board_name: str | None = None,
    create_board: Any | None = None,
) -> Path:
    """Complete first-use selection, creating a board before config persistence.

    The interactive `/ginflow` skill supplies ``choice`` and ``board_name`` and
    passes a native Kanban board-creation operation as ``create_board``. Keeping
    the decision and side effect behind this small API makes the ordering and
    fail-closed behavior deterministic in tests.
    """
    workspace = Path(workspace).expanduser().resolve()
    path = config_path(workspace)
    if path.exists():
        raise ContextInitializationError(f"project config already exists: {path}")
    if choice == "current":
        board = (current_board or "").strip()
        if not board:
            raise ContextInitializationError("current/default Kanban board is unavailable")
    elif choice == "new":
        board = (board_name or "").strip()
        if not board:
            raise ContextInitializationError("new board name must not be empty")
        if not callable(create_board):
            raise ContextInitializationError("native Kanban board creation is required")
        created = create_board(board)
        if isinstance(created, str) and created.strip():
            board = created.strip()
        elif created is not True:
            raise ContextInitializationError("native Kanban board creation failed")
    else:
        raise ContextInitializationError("choose the current/default board or create a new board")
    persisted = persist_context(workspace, board=board)
    if persisted is None:
        raise ContextInitializationError(f"unable to persist project config: {path}")
    return persisted


__all__ = ["CONFIG_RELATIVE_PATH", "CONFIG_VERSION", "ContextInitializationError", "active_board", "config_exists", "config_path", "configured_context", "context_error", "context_mismatch", "initialize_context", "load_config", "persist_context", "resolve_board"]
