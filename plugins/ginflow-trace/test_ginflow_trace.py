"""Focused tests for the standalone Ginflow trace package."""

from __future__ import annotations

import json
import os
import sys
from types import SimpleNamespace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from ginflow_trace.decorator import trace
from ginflow_trace.identity import resolve_identity
from ginflow_trace.sanitize import sanitize
from ginflow_trace.storage import append_record


def test_identity_filenames():
    known = resolve_identity((), {"session_worker_id": "session-1", "task_id": "task-2"})
    assert known.filename == "session-1__task-2.json"
    unknown = resolve_identity((), {"task_id": "task-2"})
    assert unknown.filename.startswith("unknown__task-2__") and unknown.filename.endswith(".json")


def test_identity_prefers_hook_context():
    context = SimpleNamespace(session_worker_id="hook-session", kanban_worker_id="hook-task")
    identity = resolve_identity((context,), {"session_worker_id": "argument-session"})
    assert identity.filename == "argument-session__hook-task.json"


def test_storage_appends_valid_json():
    with TemporaryDirectory() as directory:
        root = Path(directory)
        append_record(root, "worker__task.json", {"timestamp": "now", "function": "one"})
        append_record(root, "worker__task.json", {"timestamp": "later", "function": "two"})
        records = json.loads((root / "worker__task.json").read_text())
        assert isinstance(records, list)
        assert [record["function"] for record in records] == ["one", "two"]


def test_sanitizes_sensitive_and_large_values():
    value = sanitize({"api_key": "secret", "body": "x" * 5000})
    assert isinstance(value, dict)
    assert value["api_key"] == "<redacted>"
    assert value["body"].endswith("<truncated>")


def test_disabled_trace_is_noop():
    old = os.environ.pop("GINFLOW_LOG", None)
    try:
        calls = []

        @trace
        def function(value):
            calls.append(value)
            return value + 1

        assert function(1) == 2
        assert calls == [1]
    finally:
        if old is not None:
            os.environ["GINFLOW_LOG"] = old


def test_trace_error_does_not_replace_function_error():
    old = os.environ.get("GINFLOW_LOG")
    os.environ["GINFLOW_LOG"] = "1"
    try:
        @trace
        def function():
            raise ValueError("expected")

        try:
            function()
        except ValueError as error:
            assert str(error) == "expected"
        else:
            raise AssertionError("function exception was swallowed")
    finally:
        if old is None:
            os.environ.pop("GINFLOW_LOG", None)
        else:
            os.environ["GINFLOW_LOG"] = old


def test_trace_write_failure_is_non_blocking_and_recorded():
    old = os.environ.get("GINFLOW_LOG")
    os.environ["GINFLOW_LOG"] = "1"
    try:
        import ginflow_trace.decorator as decorator

        writes = []

        def failing_append(root, filename, record):
            writes.append((root.name, record["status"]))
            if root.name == "logs":
                raise OSError("disk full")

        @trace
        def function():
            return "result"

        with patch.object(decorator, "append_record", failing_append):
            assert function() == "result"
        assert writes == [("logs", "success"), ("errors", "trace_error")]
    finally:
        if old is None:
            os.environ.pop("GINFLOW_LOG", None)
        else:
            os.environ["GINFLOW_LOG"] = old


if __name__ == "__main__":
    for name, function in sorted(globals().items()):
        if name.startswith("test_"):
            function()
    print("PASS: ginflow trace")
