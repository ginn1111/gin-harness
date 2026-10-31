#!/usr/bin/env python3
"""Native Herdr popup for workspace-local Hermes Plan Mode files."""

import curses
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import unicodedata

PLUGIN_ID = "gin.hermes-plans"
# ponytail: CLI arguments cap plans at 64 KiB; use socket transport for larger plans.
MAX_BYTES = 64 * 1024


def herdr(*args):
    try:
        result = subprocess.run(
            [os.environ.get("HERDR_BIN_PATH", "herdr"), *args],
            capture_output=True, text=True, timeout=15,
        )
    except subprocess.TimeoutExpired as exc:
        raise ValueError("Herdr timed out; delivery may be uncertain. Inspect agent before retrying.") from exc
    if result.returncode:
        raise ValueError(result.stderr.strip() or result.stdout.strip() or "Herdr command failed")
    data = json.loads(result.stdout)
    if not isinstance(data, dict) or "error" in data or not isinstance(data.get("result"), dict):
        raise ValueError("Herdr returned an error or invalid response")
    return data["result"]


def snapshot(pane_id):
    agent = herdr("agent", "get", pane_id)["agent"]
    process = herdr("pane", "process-info", "--pane", pane_id)["process_info"]
    if agent.get("pane_id") != pane_id or not agent.get("agent") or not agent.get("terminal_id"):
        raise ValueError("Invoking pane has no recognized agent")
    group = process.get("foreground_process_group_id")
    foreground = process.get("foreground_processes", [])
    names = {agent["agent"], agent["agent"] + ".exe", agent["agent"] + ".js"}
    if not group or group == process.get("shell_pid") or not any(
        Path(arg).name in names for p in foreground for arg in p.get("argv", [])
    ):
        raise ValueError("Agent is not in foreground; refusing shell or suspended-agent input")
    return {
        "pane_id": pane_id, "terminal_id": agent["terminal_id"],
        "agent": agent["agent"], "session": agent.get("agent_session"),
        "process_group": group, "pids": sorted(p["pid"] for p in foreground),
        "cwd": agent.get("foreground_cwd") or agent.get("cwd"),
    }, agent.get("agent_status")


def plan_root(cwd):
    if not isinstance(cwd, str) or not Path(cwd).is_absolute():
        raise ValueError("Herdr did not supply an absolute agent working directory")
    workspace = Path(cwd).resolve(strict=True)
    root = workspace / ".hermes" / "plans"
    if root.parent.is_symlink() or root.is_symlink():
        raise ValueError("Plan directory must not be a symlink")
    if not root.is_dir():
        raise ValueError(f"No Hermes plans in {root}")
    return root


def read_plan(root, path):
    relative = path.relative_to(root)
    if not relative.parts or ".." in relative.parts or path.suffix != ".md":
        raise ValueError("Invalid plan path")
    # Walk through directory descriptors so symlink swaps cannot escape the plan root.
    fd = os.open(root.parent.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in (".hermes", "plans", *relative.parts[:-1]):
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        plan_fd = os.open(relative.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        with os.fdopen(plan_fd, "rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise ValueError("Plan must be a regular file")
            raw = stream.read(MAX_BYTES + 1)
    finally:
        os.close(fd)
    if len(raw) > MAX_BYTES:
        raise ValueError("Plan exceeds 64 KiB; nothing sent")
    text = raw.decode("utf-8")
    if not text.strip():
        raise ValueError("Plan is empty")
    if any(unicodedata.category(ch) == "Cc" and ch not in "\n\r\t" for ch in text):
        raise ValueError("Plan contains unsafe terminal control characters")
    return text


def plans(root):
    found = []
    for directory, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [name for name in dirs if not (Path(directory) / name).is_symlink()]
        for name in files:
            path = Path(directory) / name
            if path.suffix == ".md" and not path.is_symlink() and path.is_file():
                found.append(path)
    return sorted(found, key=lambda path: path.relative_to(root).as_posix().casefold())


def submit(target, text):
    current, status = snapshot(target["pane_id"])
    if current != target:
        raise ValueError("Agent or working directory changed; reopen picker")
    if status not in {"idle", "done"}:
        raise ValueError(f"Agent is {status or 'unknown'}; wait until it is idle")
    # Herdr uses fixed positional arguments and does not accept a '--' separator.
    herdr("agent", "prompt", target["pane_id"], text)


def line(screen, row, text, style=0):
    height, width = screen.getmaxyx()
    if 0 <= row < height and width > 1:
        text = "".join(ch if ch.isprintable() else " " for ch in text)
        try:
            screen.addnstr(row, 0, text, width - 1, style)
        except curses.error:
            pass  # A resize or double-width character can hit the last column.


def message(screen, text):
    screen.erase()
    for row, value in enumerate(str(text).splitlines()):
        line(screen, row, value)
    line(screen, screen.getmaxyx()[0] - 1, "Press any key to close")
    screen.refresh()
    screen.getch()


def picker(screen, target):
    screen.keypad(True)
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    root = plan_root(target["cwd"])
    files = plans(root)
    if not files:
        message(screen, f"No Markdown plans in {root}")
        return
    selected, scroll = 0, 0
    while True:
        height, _ = screen.getmaxyx()
        count = max(1, (height - 6) // 3)
        start = selected // count * count
        screen.erase()
        line(screen, 0, f"Hermes Plans | {target['agent']} | {target['pane_id']}", curses.A_BOLD)
        line(screen, 1, "Up/Down select | Left/Right preview | Enter send | Esc cancel")
        for row, path in enumerate(files[start:start + count], 3):
            chosen = path == files[selected]
            line(screen, row, str(path.relative_to(root)), curses.A_REVERSE if chosen else 0)
        try:
            content = read_plan(root, files[selected])
            error = None
        except (OSError, ValueError) as exc:
            content, error = "", str(exc)
        preview = content.expandtabs(4).splitlines()
        preview_rows = max(1, height - count - 6)
        scroll = min(scroll, max(0, len(preview) - preview_rows))
        line(screen, count + 3, f"Preview ({scroll + 1}/{max(1, len(preview))})", curses.A_BOLD)
        for row, value in enumerate(preview[scroll:scroll + preview_rows], count + 4):
            line(screen, row, value)
        line(screen, height - 1, error or str(files[selected].relative_to(root)))
        screen.refresh()
        key = screen.getch()
        if key in (27, 3):
            return
        if key in (curses.KEY_UP, curses.KEY_DOWN):
            selected = (selected + (1 if key == curses.KEY_DOWN else -1)) % len(files)
            scroll = 0
        elif key in (curses.KEY_LEFT, curses.KEY_RIGHT):
            scroll = max(0, scroll + (preview_rows if key == curses.KEY_RIGHT else -preview_rows))
        elif key in (10, 13, curses.KEY_ENTER) and error is None:
            try:
                # Send exactly the snapshot rendered above, even if file changes while waiting.
                submit(target, content)
            except (OSError, ValueError, KeyError, TypeError) as exc:
                message(screen, f"Send failed: {exc}\nDelivery may be uncertain; inspect agent before retrying.")
            return


def run_popup(screen):
    try:
        picker(screen, json.loads(os.environ["HERDR_HERMES_PLAN_TARGET"]))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        message(screen, exc)


def main():
    plugin_context = os.environ.get("HERDR_PLUGIN_ID") == PLUGIN_ID and os.environ.get("HERDR_SOCKET_PATH")
    if os.environ.get("HERDR_ENV") != "1" and not plugin_context:
        raise ValueError("Run this plugin inside Herdr")
    if sys.argv[1:] == ["open"]:
        context = json.loads(os.environ["HERDR_PLUGIN_CONTEXT_JSON"])
        pane_id = context.get("focused_pane_id")
        if not isinstance(pane_id, str) or not pane_id or pane_id.startswith("-"):
            raise ValueError("Invoke from an agent pane")
        target, _ = snapshot(pane_id)
        herdr("plugin", "pane", "open", "--plugin", PLUGIN_ID, "--entrypoint", "picker",
              "--target-pane", pane_id, "--focus",
              "--env", "HERDR_HERMES_PLAN_TARGET=" + json.dumps(target))
    elif sys.argv[1:] == ["pick"]:
        curses.wrapper(run_popup)
    else:
        raise ValueError("Usage: picker.py open|pick")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, curses.error) as exc:
        print(f"Hermes Plans: {exc}", file=sys.stderr)
        if sys.argv[1:] == ["open"] and os.environ.get("HERDR_SOCKET_PATH"):
            try:
                herdr("notification", "show", "Hermes Plans", "--body", str(exc), "--sound", "none")
            except (OSError, ValueError):
                pass
        sys.exit(1)
