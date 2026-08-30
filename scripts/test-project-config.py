#!/usr/bin/env python3
import os
import tempfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/ginflow/lib"))
import project_config
from project_config import (
    CONFIG_RELATIVE_PATH,
    WORKER_FIELDS,
    ContextInitializationError,
    WorkerDefaultsError,
    config_exists,
    config_path,
    configured_worker,
    context_error,
    configured_context,
    initialize_context,
    persist_context,
    persist_worker_defaults,
    resolve_board,
    resolve_worker_dispatch,
    worker_error,
)

with tempfile.TemporaryDirectory() as directory:
    target = Path(directory)
    assert CONFIG_RELATIVE_PATH == Path(".ginflow.yaml")
    assert config_path(target) == target.resolve() / ".ginflow.yaml"
    assert resolve_board(target, explicit="explicit") == "explicit"
    assert not config_exists(target)
    assert resolve_board(target, env={"HERMES_KANBAN_BOARD": "env"}) == "env"
    path = persist_context(target, board="project")
    assert path == config_path(target)
    assert config_exists(target)
    assert configured_context(target) == {"board": "project", "workspace": str(target.resolve())}
    assert resolve_board(target, env={}) == "project"
    assert resolve_board(target, explicit="override", env={"HERMES_KANBAN_BOARD": "env"}) == "override"
    assert persist_context(target / "missing", board="ignored") is None
    assert context_error(target) is None

    config_path(target).write_text(
        "version: 1\nginflow:\n  board: project\n  workspace: .\n"
    )
    assert context_error(target) == "project config ginflow.workspace must be an absolute path"
    config_path(target).unlink()

    atomic_failure = target / "atomic-failure"
    atomic_failure.mkdir()
    original_replace = project_config.os.replace
    project_config.os.replace = lambda *_: (_ for _ in ()).throw(OSError("replace failed"))
    try:
        assert persist_context(atomic_failure, board="project") is None
    finally:
        project_config.os.replace = original_replace
    assert not config_path(atomic_failure).exists()
    assert not config_path(atomic_failure).with_name(".ginflow.yaml.tmp").exists()

    selected = target / "selected"
    selected.mkdir()
    selected_path = initialize_context(
        selected, choice="current", current_board="default"
    )
    assert selected_path == config_path(selected)
    assert configured_context(selected)["board"] == "default"

    created = target / "created"
    created.mkdir()
    calls = []
    created_path = initialize_context(
        created,
        choice="new",
        current_board="default",
        board_name="project-board",
        create_board=lambda name: calls.append(name) or True,
    )
    assert calls == ["project-board"]
    assert configured_context(created)["board"] == "project-board"
    assert created_path == config_path(created)

    for kwargs in (
        {"choice": "new", "current_board": "default", "board_name": "  ", "create_board": lambda _: True},
        {"choice": "new", "current_board": "default", "board_name": "new", "create_board": lambda _: False},
        {"choice": "current", "current_board": None},
    ):
        failed = target / f"failed-{len(list(target.iterdir()))}"
        failed.mkdir()
        try:
            initialize_context(failed, **kwargs)
        except ContextInitializationError:
            assert not config_path(failed).exists()
        else:
            raise AssertionError("unsafe initialization unexpectedly succeeded")

    config_path(target).write_text("version: 1\nginflow:\n  board: project\n  workspace: /other/project\n")
    assert context_error(target) == (
        f"project config workspace /other/project does not match {target.resolve()}"
    )
    assert resolve_board(target, explicit="override", env={"HERMES_KANBAN_BOARD": "env"}) is None

    config_path(target).write_text("not: [valid")
    assert context_error(target).startswith("project config is malformed:")
    assert resolve_board(target, env={"HERMES_KANBAN_BOARD": "env"}) is None

    # Worker dispatch defaults are optional and never invalidate context.
    assert worker_error(target) is None
    assert configured_worker(target) == {}
    assert resolve_worker_dispatch(target, current_profile="active") == {"profile": "active"}
    assert resolve_worker_dispatch(
        target, explicit={"profile": "override"}, current_profile="active"
    ) == {"profile": "override"}

    ws_worker = target / "worker"
    ws_worker.mkdir()
    persist_context(ws_worker, board="project")
    assert worker_error(ws_worker) is None
    assert configured_worker(ws_worker) == {}
    assert resolve_worker_dispatch(ws_worker, current_profile="active") == {"profile": "active"}

    # Persisting a complete worker block preserves board/workspace/version.
    worker_path = persist_worker_defaults(
        ws_worker,
        profile="ginb",
        provider="openai-codex",
        model="gpt-5.6-luna",
    )
    assert worker_path == config_path(ws_worker)
    assert configured_worker(ws_worker) == {
        "profile": "ginb",
        "provider": "openai-codex",
        "model": "gpt-5.6-luna",
    }
    assert configured_context(ws_worker)["board"] == "project"
    assert worker_error(ws_worker) is None
    assert resolve_worker_dispatch(ws_worker, current_profile="active") == {
        "profile": "ginb",
        "provider": "openai-codex",
        "model": "gpt-5.6-luna",
    }
    assert resolve_worker_dispatch(
        ws_worker,
        explicit={"provider": "anthropic", "model": "sonnet"},
        current_profile="active",
    ) == {"profile": "ginb", "provider": "anthropic", "model": "sonnet"}

    # Malformed worker values block resolution but not read-only context.
    config_path(ws_worker).write_text(
        "version: 1\nginflow:\n"
        "  board: project\n"
        f"  workspace: {ws_worker.resolve()}\n"
        "  worker:\n"
        "    profile: 42\n"
    )
    assert worker_error(ws_worker) == "ginflow.worker.profile must be a non-empty string"
    assert context_error(ws_worker) is None
    try:
        resolve_worker_dispatch(ws_worker, current_profile="active")
    except WorkerDefaultsError:
        pass
    else:
        raise AssertionError("invalid worker defaults unexpectedly resolved")

    config_path(ws_worker).write_text(
        "version: 1\nginflow:\n"
        "  board: project\n"
        f"  workspace: {ws_worker.resolve()}\n"
        "  worker:\n"
        "    profile: ginb\n"
        "    provider: openai-codex\n"
        "    model: gpt-5.6-luna\n"
    )
    assert worker_error(ws_worker) is None

    # Empty/unknown worker fields fail closed.
    config_path(ws_worker).write_text(
        "version: 1\nginflow:\n"
        "  board: project\n"
        f"  workspace: {ws_worker.resolve()}\n"
        "  worker:\n"
        "    profile: \"\"\n"
    )
    assert worker_error(ws_worker) == "ginflow.worker.profile must be a non-empty string"
    config_path(ws_worker).write_text(
        "version: 1\nginflow:\n"
        "  board: project\n"
        f"  workspace: {ws_worker.resolve()}\n"
        "  worker:\n"
        "    profile: ginb\n"
        "    extra: unexpected\n"
    )
    assert worker_error(ws_worker) == "ginflow.worker has unknown fields: extra"

    # Persistence must not proceed on an invalid/missing context.
    assert persist_worker_defaults(
        target, profile="ginb", provider="openai-codex", model="gpt-5.6-luna"
    ) is None

    # Partial persistence values are rejected atomically.
    ws_partial = target / "worker-partial"
    ws_partial.mkdir()
    persist_context(ws_partial, board="project")
    assert persist_worker_defaults(ws_partial, profile="ginb", provider="", model="x") is None
    assert configured_worker(ws_partial) == {}

print("project config precedence and persistence passed")
