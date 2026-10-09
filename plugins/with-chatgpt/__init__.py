"""Native Hermes plugin for explicit ChatGPT planning and review collaboration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .cli import handle_command, setup_parser
from .hook import pre_llm_call
from .state import clear_session

_PLUGIN_ROOT = Path(__file__).resolve().parent


def _on_session_end(*, session_id: str = "", state: Any = None, **_: Any) -> None:
    try:
        if state is not None:
            clear_session(state, session_id)
    except Exception:
        return None


def _handle_command(args: Any, ctx: Any) -> None:
    handle_command(args, ctx)


def _pre_llm_call(ctx: Any, **kwargs: Any) -> dict[str, str] | None:
    payload = dict(kwargs)
    payload.pop("state", None)
    return pre_llm_call(state=ctx.state, **payload)


def _session_end(ctx: Any, **kwargs: Any) -> None:
    payload = dict(kwargs)
    payload.pop("state", None)
    _on_session_end(state=ctx.state, **payload)


def register(ctx: Any) -> None:
    ctx.register_hook("pre_llm_call", lambda **kwargs: _pre_llm_call(ctx, **kwargs))
    ctx.register_hook("on_session_end", lambda **kwargs: _session_end(ctx, **kwargs))
    ctx.register_cli_command(
        "with-chatgpt",
        help="Manage Hermes with ChatGPT collaboration",
        setup_fn=setup_parser,
        handler_fn=lambda args: _handle_command(args, ctx),
        description="Hermes with ChatGPT: ChatGPT plans and reviews; Hermes executes; C2C observes read-only workspace state.",
    )
    ctx.register_skill(
        "c2c",
        _PLUGIN_ROOT / "skills" / "c2c" / "SKILL.md",
        description="Use C2C for explicit ChatGPT planning/review and read-only workspace observation.",
        frontmatter={"name": "c2c", "description": "Hermes with ChatGPT collaboration workflow."},
    )
    ctx.register_skill(
        "terminal-browser",
        _PLUGIN_ROOT / "skills" / "terminal-browser" / "SKILL.md",
        description="Drive external terminal-browser explicitly for ChatGPT workflow steps.",
        frontmatter={"name": "terminal-browser", "description": "External browser guidance for C2C."},
    )


__all__ = ["register", "pre_llm_call"]
