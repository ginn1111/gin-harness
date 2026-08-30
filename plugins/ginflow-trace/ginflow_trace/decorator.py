"""Non-blocking function-call tracing decorator."""

from __future__ import annotations

import functools
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, TypeVar, cast

from .identity import resolve_identity
from .sanitize import sanitize
from .storage import append_record

F = TypeVar("F", bound=Callable[..., Any])
ROOT = Path(__file__).resolve().parents[1]


def _enabled() -> bool:
    """Tracing is on when GINFLOW_LOG=1 or the project config enables ginflow.trace."""
    if os.environ.get("GINFLOW_LOG") == "1":
        return True
    if os.environ.get("GINFLOW_LOG") is not None:
        return False
    return _config_trace_enabled()


def _config_trace_enabled() -> bool:
    """Read ginflow.trace from the nearest .ginflow.yaml above the package."""
    config = _find_config(ROOT.parents[1])
    if config is None:
        return False
    context = config.get("ginflow")
    if not isinstance(context, dict):
        return False
    value = context.get("trace")
    return value is True


def _read_config(file: Path) -> dict | None:
    try:
        import yaml
    except ImportError:
        return None
    try:
        data = yaml.safe_load(file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _find_config(start: Path) -> dict | None:
    path = Path(start).expanduser().resolve()
    while True:
        candidate = path / ".ginflow.yaml"
        if candidate.is_file():
            data = _read_config(candidate)
            if data is not None:
                return data
        if path.parent == path:
            return None
        path = path.parent


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _write(directory: str, identity, record: dict[str, Any]) -> None:
    try:
        append_record(ROOT / directory, identity.filename, record)
    except Exception as error:  # tracing must never affect the wrapped function
        try:
            if directory != "errors":
                append_record(
                    ROOT / "errors",
                    identity.filename,
                    {
                        "timestamp": _timestamp(),
                        "function": record.get("function", "unknown"),
                        "status": "trace_error",
                        "error_type": type(error).__name__,
                        "message": sanitize(str(error)),
                    },
                )
        except Exception:
            pass
        try:
            print(f"ginflow-trace: unable to write {directory}: {type(error).__name__}", file=sys.stderr)
        except Exception:
            pass


def trace(function: F) -> F:
    """Trace a function when enabled; preserve its behavior if tracing fails."""
    @functools.wraps(function)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        if not _enabled():
            return function(*args, **kwargs)
        identity = resolve_identity(args, kwargs)
        base: dict[str, Any] = {"timestamp": _timestamp(), "function": function.__name__}
        try:
            result = function(*args, **kwargs)
        except Exception as error:
            _write("errors", identity, base | {
                "input": sanitize({"args": args, "kwargs": kwargs}),
                "status": "error",
                "error_type": type(error).__name__,
                "message": sanitize(str(error)),
            })
            raise
        _write("logs", identity, base | {
            "input": sanitize({"args": args, "kwargs": kwargs}),
            "output": sanitize(result),
            "status": "success",
        })
        return result
    return cast(F, wrapped)
