"""Hermes plugin CLI: explicit lifecycle only."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .state import active_session_count, disable_session, enable_session, session_enabled

PLUGIN_ROOT = Path(__file__).resolve().parent
C2C_ROOT = PLUGIN_ROOT / "c2c"
C2C_PACKAGE = C2C_ROOT / "package.json"


def _json(value: dict[str, Any]) -> None:
    print(json.dumps(value, sort_keys=True))


def _session_id(args: argparse.Namespace) -> str:
    value = args.session_id or os.environ.get("HERMES_SESSION_ID", "")
    if not value.strip():
        raise ValueError("session id is required; pass --session-id or set HERMES_SESSION_ID")
    return value.strip()


def _node_version() -> tuple[bool, str]:
    node = shutil.which("node")
    if not node:
        return False, "node executable not found (install Node.js >= 20)"
    try:
        result = subprocess.run([node, "--version"], capture_output=True, text=True, timeout=3, check=False)
    except (OSError, subprocess.TimeoutExpired) as error:
        return False, f"could not run Node.js: {error}"
    version = result.stdout.strip() or result.stderr.strip()
    try:
        major = int(version.lstrip("v").split(".", 1)[0])
    except (ValueError, IndexError):
        return False, f"could not parse Node.js version: {version}"
    return major >= 20, version


def _browser_check() -> tuple[bool, str]:
    browser = shutil.which("terminal-browser")
    return (True, browser) if browser else (False, "terminal-browser executable not found; install it separately")


def _package_check() -> tuple[bool, str]:
    if not C2C_PACKAGE.is_file():
        return False, f"C2C package missing: {C2C_PACKAGE}"
    dist_entry = C2C_ROOT / "dist" / "cli" / "index.js"
    if dist_entry.is_file():
        return True, f"built runtime: {dist_entry}"
    if not (C2C_ROOT / "node_modules").is_dir():
        return False, "C2C build missing and dependencies unavailable; run pnpm install and pnpm build in the C2C package"
    return False, "C2C build missing; run pnpm build in the C2C package"


def _run_c2c(args: list[str], *, timeout: int = 15) -> subprocess.CompletedProcess[str]:
    node = shutil.which("node")
    if not node:
        raise RuntimeError("node executable not found (install Node.js >= 20)")
    dist_entry = C2C_ROOT / "dist" / "cli" / "index.js"
    if dist_entry.is_file():
        command = [node, str(dist_entry), *args]
    else:
        entry = C2C_ROOT / "src" / "cli" / "index.ts"
        command = [node, "--import", "tsx", str(entry), *args]
    try:
        return subprocess.run(command, cwd=C2C_ROOT, text=True, capture_output=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(f"C2C command timed out after {timeout}s") from error
    except OSError as error:
        raise RuntimeError(f"could not start C2C: {error}") from error


def _parse_json_output(completed: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    try:
        data = json.loads(completed.stdout)
    except json.JSONDecodeError:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"exit status {completed.returncode}"
        return {"ok": False, "error": detail, "exit_status": completed.returncode}
    if not isinstance(data, dict):
        return {"ok": False, "error": "C2C returned a non-object JSON result", "exit_status": completed.returncode}
    if completed.returncode != 0:
        data.setdefault("ok", False)
        data.setdefault("exit_status", completed.returncode)
    return data


def _c2c_json(action: str, workspace: str | None = None) -> dict[str, Any]:
    forwarded = [action, "--json"]
    if workspace:
        forwarded += ["--workspace", workspace]
    try:
        return _parse_json_output(_run_c2c(forwarded, timeout=30))
    except (RuntimeError, OSError) as error:
        return {"ok": False, "error": str(error)}


def _doctor(workspace: str | None, repair: bool) -> dict[str, Any]:
    args = ["doctor", "--json"]
    if workspace:
        args += ["--workspace", workspace]
    if repair:
        args += ["--repair"]
    try:
        data = _parse_json_output(_run_c2c(args, timeout=30))
    except (RuntimeError, OSError) as error:
        data = {"ok": False, "error": str(error)}
    data["repair_requested"] = repair
    data["mutating"] = repair
    return data


def _forwarded_result(action: str, workspace: str | None, json_output: bool) -> dict[str, Any]:
    forwarded = [action]
    if workspace:
        forwarded += ["--workspace", workspace]
    if json_output:
        forwarded.append("--json")
    try:
        completed = _run_c2c(forwarded, timeout=30)
    except (RuntimeError, OSError) as error:
        return {"ok": False, "action": action, "error": str(error), "mutating": action in {"pair", "stop"}}
    return {
        "ok": completed.returncode == 0,
        "action": action,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "mutating": action in {"pair", "stop"},
    }


def _setup_result() -> dict[str, Any]:
    node_ok, node_detail = _node_version()
    package_ok, package_detail = _package_check()
    browser_ok, browser_detail = _browser_check()
    return {
        "ok": node_ok and package_ok and browser_ok,
        "action": "setup",
        "node": {"ok": node_ok, "detail": node_detail},
        "c2c": {"ok": package_ok, "detail": package_detail},
        "terminal_browser": {"ok": browser_ok, "detail": browser_detail},
        "repair_required": False,
    }


def setup_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("action", choices=["setup", "doctor", "enable", "disable", "status", "pair", "stop"])
    parser.add_argument("--session-id")
    parser.add_argument("--workspace")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--repair", action="store_true")


def handle_command(args: argparse.Namespace, ctx: Any) -> None:
    action = args.action
    if args.repair and action != "doctor":
        raise ValueError("--repair is only valid with doctor")
    if action == "enable":
        session = _session_id(args)
        enable_session(ctx.state, session)
        result = {"ok": True, "action": action, "session_id": session, "enabled": True}
    elif action == "disable":
        session = _session_id(args)
        disable_session(ctx.state, session)
        result = {"ok": True, "action": action, "session_id": session, "enabled": False}
    elif action == "status":
        session = args.session_id or os.environ.get("HERMES_SESSION_ID", "")
        observation = _c2c_json("status", args.workspace)
        result = {
            "ok": observation.get("ok", False),
            "action": action,
            "profile": ctx.profile_name,
            "enabled": session_enabled(ctx.state, session),
            "active_sessions": active_session_count(ctx.state),
            "bridge": observation,
            "state": observation.get("state", "unknown"),
        }
    elif action == "setup":
        result = _setup_result()
    elif action == "doctor":
        result = _doctor(args.workspace, args.repair)
    else:
        result = _forwarded_result(action, args.workspace, args.json)

    # Keep plugin command output machine-readable even when the nested runtime is unavailable.
    if action == "status" and not result.get("ok", False):
        result.setdefault("state", "unknown")
        result.setdefault("bridge", {"ok": False, "state": result["state"]})
        result.setdefault("profile", ctx.profile_name)
        result.setdefault("enabled", session_enabled(ctx.state, args.session_id or os.environ.get("HERMES_SESSION_ID", "")))
        result.setdefault("active_sessions", active_session_count(ctx.state))
    if args.json:
        _json(result)
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    if not result.get("ok", False):
        raise SystemExit(1)
