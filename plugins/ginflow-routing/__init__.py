"""Inject Kanban board state before LLM calls to route ginflow agents.

When ginflow skill is loaded, this plugin runs on every pre_llm_call hook
and injects the current Kanban board snapshot — card count, titles, statuses —
so the agent can route itself to work shaping (no cards) or resume (cards exist).

The injected context is ephemeral (per-turn) and never persisted to the session DB.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
from typing import Any

logger = logging.getLogger(__name__)


def _kanban_board_state() -> str | None:
    """Return a snapshot of the Kanban board as concise text, or None."""
    try:
        result = subprocess.run(
            ["hermes", "kanban", "list", "--json"],
            text=True,
            capture_output=True,
            timeout=15,
        )
    except FileNotFoundError:
        return None
    except OSError as exc:
        logger.warning("ginflow-routing: kanban list unavailable: %s", exc)
        return None
    except subprocess.TimeoutExpired:
        return None

    if result.returncode != 0:
        # Board not initialised yet — that's fine, treat as empty.
        return None

    if not result.stdout.strip():
        return None

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None

    tasks = data if isinstance(data, list) else data.get("tasks", data.get("items", [data]))
    if not tasks:
        return None

    lines: list[str] = []
    for task in tasks:
        tid = task.get("id", "?")
        title = task.get("title", "?")
        status = task.get("status", "?")
        assignee = task.get("assignee") or ""
        workspace = task.get("workspace_path") or ""
        ws_suffix = f" @ {workspace}" if workspace else ""
        assign_suffix = f" [{assignee}]" if assignee else ""
        lines.append(f"- {tid}: {title} ({status}){assign_suffix}{ws_suffix}")

    return "\n".join(lines) if lines else None


def _routing_context(**kwargs: Any) -> dict[str, str] | str | None:
    """Inject board state into the user message when ginflow context is active.

    The context text tells the agent how many cards exist and their statuses.
    If no cards exist, the agent routes to shaping. If cards exist, it resumes.
    """
    # Always check board state — cheap single subprocess call.
    # Kanban-dispatched sessions have HERMES_KANBAN_TASK set;
    # non-dispatched sessions also get routing context when cards exist.
    board = _kanban_board_state()
    if board is None:
        # Board not initialised — agent should shape first card.
        context = (
            "[ginflow-routing: Kanban board is empty or uninitialised. "
            "No existing cards found. Route to work shaping: "
            "investigate the current repo, choose work mode "
            "(investigation/implementation/brainstorming), choose artifact level, "
            "and draft a Kanban card.]"
        )
    else:
        context = (
            "[ginflow-routing: Kanban board has active cards.\n"
            f"{board}\n"
            "Route to resume: read the selected/active card, "
            "confirm required fields (objective, scope, acceptance, workspace, assignee, links), "
            "read linked artifacts, check git state, run project baseline, "
            "then execute.]"
        )

    return {"context": context}


def register(ctx) -> None:
    ctx.register_hook("pre_llm_call", _routing_context)
