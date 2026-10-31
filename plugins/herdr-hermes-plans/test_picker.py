#!/usr/bin/env python3
"""Run with python3 plugins/herdr-hermes-plans/test_picker.py."""

import copy
import json
import os
from pathlib import Path
import pty
import select
import subprocess
import sys
import tempfile
import time
import tomllib

import picker


def rejects(call):
    try:
        call()
    except (OSError, ValueError):
        return
    raise AssertionError("Unsafe operation accepted")


def terminal_run(target, key):
    master, slave = pty.openpty()
    env = {**os.environ, "TERM": "xterm", "HERDR_HERMES_PLAN_TARGET": json.dumps(target)}
    manifest = tomllib.loads(Path(__file__).with_name("herdr-plugin.toml").read_text())
    child = subprocess.Popen(manifest["panes"][0]["command"],
                             stdin=slave, stdout=slave, stderr=slave, env=env)
    os.close(slave)
    output = b""
    try:
        deadline = time.monotonic() + 5
        while b"Preview" not in output and time.monotonic() < deadline:
            if select.select([master], [], [], 0.1)[0]:
                output += os.read(master, 65536)
        assert b"Preview" in output, output
        os.write(master, key)
        assert child.wait(timeout=5) == 0
    finally:
        if child.poll() is None:
            child.kill()
            child.wait()
        os.close(master)


def main():
    manifest = tomllib.loads(Path(__file__).with_name("herdr-plugin.toml").read_text())
    assert manifest["id"] == picker.PLUGIN_ID
    assert manifest["panes"][0]["placement"] == "popup"
    with tempfile.TemporaryDirectory() as directory:
        base = Path(directory)
        root = base / ".hermes" / "plans"
        root.mkdir(parents=True)
        chosen = root / "01 plan with spaces.md"
        literal = "--literal\n# Plan\nDo not execute $(touch SHOULD_NOT_EXIST) or `echo shell`.\n"
        chosen.write_text(literal)
        approved = root / "approved"
        approved.mkdir()
        (approved / "saved.md").write_text("Approved plan")
        (root / "ignore.json").write_text("{}")
        outside = base / "outside.md"
        outside.write_text("outside")
        (root / "escape.md").symlink_to(outside)
        (root / "escape-dir").symlink_to(base, target_is_directory=True)
        assert picker.plan_root(str(base)) == root
        assert picker.plans(root) == [chosen, approved / "saved.md"]
        assert picker.read_plan(root, chosen) == literal
        for path in (outside, root / "escape.md", root / "escape-dir" / "outside.md",
                     root / ".." / "outside.md", root / "ignore.json"):
            rejects(lambda path=path: picker.read_plan(root, path))
        bad = root / "bad.md"
        for raw in (b"", b" \n", b"\xff", b"\x00", b"\x1b[201~", b"x" * (picker.MAX_BYTES + 1)):
            bad.write_bytes(raw)
            rejects(lambda: picker.read_plan(root, bad))
        bad.unlink()
        os.mkfifo(bad)
        rejects(lambda: picker.read_plan(root, bad))
        bad.unlink()
        original = root.rename(root.with_name("original"))
        root.symlink_to(original, target_is_directory=True)
        rejects(lambda: picker.plan_root(str(base)))
        rejects(lambda: picker.read_plan(root, chosen))
        root.unlink()
        original.rename(root)

        state_path, log_path = base / "state.json", base / "calls.jsonl"
        state = {
            "agent": {"pane_id": "w1:p2", "agent": "hermes", "terminal_id": "term_2",
                      "agent_session": {"value": "session-1"}, "agent_status": "idle",
                      "foreground_cwd": str(base)},
            "process_info": {"shell_pid": 1, "foreground_process_group_id": 2,
                             "foreground_processes": [{"pid": 2, "argv": ["python", "/bin/hermes"]}]},
        }
        state_path.write_text(json.dumps(state))
        fake = base / "herdr"
        fake.write_text("#!" + sys.executable + "\n" + '''import json, os, sys
from pathlib import Path
args = sys.argv[1:]
state = json.loads(Path(os.environ["TEST_STATE"]).read_text())
with open(os.environ["TEST_LOG"], "a") as log:
    log.write(json.dumps(args) + "\\n")
if args[:2] == ["agent", "get"]:
    result = {"agent": state["agent"]}
elif args[:2] == ["pane", "process-info"]:
    result = {"process_info": state["process_info"]}
elif args[:2] == ["agent", "prompt"]:
    assert len(args) == 4 and args[2] == "w1:p2", args
    if state.get("fail_delivery"):
        print("uncertain delivery", file=sys.stderr)
        sys.exit(1)
    result = {"submitted": True}
elif args[:3] == ["plugin", "pane", "open"]:
    result = {"opened": True}
else:
    raise AssertionError(args)
print(json.dumps({"result": result}))
''')
        fake.chmod(0o700)
        os.environ.update(HERDR_BIN_PATH=str(fake), HERDR_ENV="1", TEST_STATE=str(state_path),
                          TEST_LOG=str(log_path), HERDR_PLUGIN_ROOT=str(Path(__file__).resolve().parent),
                          HERDR_PLUGIN_CONTEXT_JSON=json.dumps({"focused_pane_id": "w1:p2"}))

        def calls():
            return [json.loads(line) for line in log_path.read_text().splitlines()]

        def prompts():
            return [args for args in calls() if args[:2] == ["agent", "prompt"]]

        plugin_env = {**os.environ, "HERDR_ENV": "", "HERDR_PLUGIN_ID": picker.PLUGIN_ID,
                      "HERDR_SOCKET_PATH": "test-socket"}
        subprocess.run(manifest["actions"][0]["command"], cwd=base, env=plugin_env, check=True)
        opened = calls()[-1]
        assert opened[:3] == ["plugin", "pane", "open"]
        target = json.loads(opened[opened.index("--env") + 1].split("=", 1)[1])
        assert target["pane_id"] == "w1:p2"
        terminal_run(target, b"\x1b")
        assert not prompts(), "Cancellation submitted a prompt"
        terminal_run(target, b"\r")
        assert prompts() == [["agent", "prompt", "w1:p2", literal]]
        assert not (base / "SHOULD_NOT_EXIST").exists()

        for change in (dict(agent_status="blocked"), dict(agent_status="working"),
                       dict(agent_status="unknown"), dict(agent_session={"value": "new"}),
                       dict(terminal_id="replacement"), dict(foreground_cwd="/tmp")):
            altered = copy.deepcopy(state)
            altered["agent"].update(change)
            state_path.write_text(json.dumps(altered))
            rejects(lambda: picker.submit(target, literal))
        altered = copy.deepcopy(state)
        altered["process_info"]["foreground_process_group_id"] = 1
        state_path.write_text(json.dumps(altered))
        rejects(lambda: picker.submit(target, literal))
        altered["process_info"]["foreground_process_group_id"] = 3
        altered["process_info"]["foreground_processes"] = [{"pid": 3, "argv": ["bash"]}]
        state_path.write_text(json.dumps(altered))
        rejects(lambda: picker.submit(target, literal))
        assert len(prompts()) == 1, "Rejected target received input"
        state_path.write_text(json.dumps({**state, "fail_delivery": True}))
        rejects(lambda: picker.submit(target, literal))
        assert len(prompts()) == 2, "Delivery failure was retried"
    print("PASS: plan files, native popup manifest, terminal selection/cancel, literal delivery, target guards, no retry")


if __name__ == "__main__":
    main()
