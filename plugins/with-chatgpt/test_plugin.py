from __future__ import annotations

import hashlib
import importlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
ROOT = Path(__file__).parent
PACKAGE_NAME = "with_chatgpt"
sys.path.insert(0, str(ROOT.parent))
import_alias = ROOT.parent / PACKAGE_NAME
if not import_alias.exists():
    import_alias.symlink_to(ROOT, target_is_directory=True)
try:
    module = importlib.import_module(PACKAGE_NAME)
    hook = importlib.import_module(f"{PACKAGE_NAME}.hook")
    state_module = importlib.import_module(f"{PACKAGE_NAME}.state")
finally:
    if import_alias.is_symlink():
        import_alias.unlink()



class State:
    def __init__(self):
        self.values = {}

    def get(self, key, default=None):
        return self.values.get(key, default)

    def set(self, key, value):
        self.values[key] = value


class Context:
    def __init__(self):
        self.hooks = []
        self.skills = []
        self.commands = []
        self.state = State()
        self.profile_name = "test"

    def register_hook(self, name, callback):
        self.hooks.append((name, callback))

    def register_skill(self, name, path, **_kwargs):
        self.skills.append((name, Path(path)))

    def register_cli_command(self, name, **kwargs):
        self.commands.append((name, kwargs))


ctx = Context()
module.register(ctx)
assert {name for name, _callback in ctx.hooks} == {"pre_llm_call", "on_session_end"}
assert {name for name, _path in ctx.skills} == {"c2c", "terminal-browser"}
assert {name for name, _entry in ctx.commands} == {"with-chatgpt"}

pre_llm = dict(ctx.hooks)["pre_llm_call"]
assert pre_llm(session_id="s1", workspace=str(ROOT)) is None
state_module.enable_session(ctx.state, " s1 ")
assert state_module.session_enabled(ctx.state, " s1 ")
state_module.disable_session(ctx.state, " s1 ")
assert not state_module.session_enabled(ctx.state, "s1")
state_module.enable_session(ctx.state, "s1")
context = pre_llm(session_id="s1", workspace=str(ROOT))
assert context and len(context["context"]) <= 2048
assert "Hermes with ChatGPT" in context["context"]
assert "token" not in context["context"].lower()

with tempfile.TemporaryDirectory() as temp:
    workspace = Path(temp)
    state_dir = workspace / "state"
    sessions = state_dir / "sessions"
    sessions.mkdir(parents=True)
    workspace_id = hashlib.sha256(str(workspace.resolve()).lower().encode()).hexdigest()[:12]
    assert hook.payload_workspace_id(workspace) == workspace_id
    checkpoint = {"checkpoint": {"protocolState": "EXECUTING", "nextExpectedStep": "Continue safely"}}
    (sessions / f"{workspace_id}.json").write_text(json.dumps(checkpoint), encoding="utf-8")
    previous = os.environ.get("C2C_STATE_DIR")
    os.environ["C2C_STATE_DIR"] = str(state_dir)
    try:
        observed = hook.pre_llm_call(state=ctx.state, session_id="s1", workspace=str(workspace))
    finally:
        if previous is None:
            os.environ.pop("C2C_STATE_DIR", None)
        else:
            os.environ["C2C_STATE_DIR"] = previous
    assert observed and "EXECUTING" in observed["context"]

    # Hermes may include a colliding state key; plugin-owned state still wins.
    colliding = ctx.hooks[0][1](session_id="s1", state={"protocolState": "BLOCKED"}, workspace=str(workspace))
    assert colliding and "INIT" in colliding["context"] and "BLOCKED" not in colliding["context"]
    # Secret-like checkpoint text must not reach model context.
    (sessions / f"{workspace_id}.json").write_text(
        json.dumps({"checkpoint": {"protocolState": "EXECUTING", "nextExpectedStep": "use bearer token=secret"}}),
        encoding="utf-8",
    )
    redacted = hook.pre_llm_call(state=ctx.state, session_id="s1", workspace=str(workspace))
    assert redacted and "bearer" not in redacted["context"].lower()

    ctx.hooks[1][1](session_id="s1")
    assert not state_module.session_enabled(ctx.state, "s1")

# Active runtime and Hermes skill surfaces stay English. Chinese README and
# historical migration docs are intentionally exempt.
import re
cjk = re.compile("[\u3000-\u303f\u4e00-\u9fff\uff00-\uffef]")
exempt = {"README.md", "README.zh-CN.md"}
active = [*ROOT.glob("*.py"), *(ROOT / "skills").rglob("*.md"), *(ROOT / "c2c" / "src").rglob("*.ts"),
          *(ROOT / "c2c" / "skill").rglob("*.md"), *(ROOT / "c2c" / "docs").glob("*.md")]
offenders = [str(f.relative_to(ROOT)) for f in active
             if f.name not in exempt and f.name != Path(__file__).name and cjk.search(f.read_text(encoding="utf-8"))]
assert not offenders, f"unintended Chinese text in active surfaces: {offenders}"

# Optional CLI failures remain structured instead of escaping through Hermes.
from with_chatgpt import cli
# Setup reports bridge/tunnel/pairing readiness read-only; unknown stays distinct.
_saved = (cli._node_version, cli._package_check, cli._browser_check, cli._c2c_json)
cli._node_version = lambda: (True, "v22")
cli._package_check = lambda: (True, "ok")
cli._browser_check = lambda: (True, "ok")
try:
    cli._c2c_json = lambda *_a, **_k: {"ok": False, "state": "unknown"}
    unknown = cli._setup_result()
    assert unknown["ok"] and not unknown["ready"] and unknown["bridge"]["state"] == "unknown"
    assert "second bridge" in unknown["next_steps"][0] and not unknown["mutating"]
    cli._c2c_json = lambda *_a, **_k: {"ok": False, "state": "stopped"}
    assert cli._setup_result()["bridge"]["state"] == "stopped"
    cli._c2c_json = lambda *_a, **_k: {"ok": True, "state": "healthy", "tunnel": {"running": True}, "tokenCount": 1}
    ready = cli._setup_result()
    assert ready["ready"] and ready["pairing"]["paired"] and not ready["next_steps"]
finally:
    cli._node_version, cli._package_check, cli._browser_check, cli._c2c_json = _saved

failed = cli._parse_json_output(subprocess.CompletedProcess([], 1, stdout="", stderr="timeout"))
assert failed["ok"] is False and failed["error"] == "timeout"
print("with-chatgpt plugin tests passed")
