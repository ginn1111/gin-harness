"""Inject Kanban board state before LLM calls to route ginflow agents.

When ginflow skill is loaded, this plugin runs on every pre_llm_call hook
and injects the current Kanban board snapshot — card count, titles, statuses —
so the agent can route itself to work shaping (no cards) or resume (cards exist).

When ginflow skill is NOT loaded, the plugin is a no-op — no subprocess call,
no context injection.

The injected context is ephemeral (per-turn) and never persisted to the session DB.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any

CORE = Path(__file__).resolve().parents[2] / "skills/ginflow/lib/harness_core.py"
import importlib.util

_spec = importlib.util.spec_from_file_location("ginflow_harness_core", CORE)
if not _spec or not _spec.loader:
    raise ImportError(f"unable to load Ginflow harness core: {CORE}")
_core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_core)
startup_gate = _core.startup_gate

logger = logging.getLogger(__name__)


def _parse_skill_list(raw: str) -> set[str]:
    """Parse comma/newline-delimited skill env values into canonical names."""
    names: set[str] = set()
    for part in raw.replace("\n", ",").split(","):
        item = part.strip()
        if item:
            names.add(item)
    return names


def _ginflow_loaded() -> bool:
    """Check if ginflow skill is active in current session."""
    try:
        import os

        active = _parse_skill_list(os.environ.get("HERMES_TUI_SKILLS", ""))
        return "ginflow" in active
    except Exception:
        return False


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
        logger.warning("ginflow-gate routing: kanban list unavailable: %s", exc)
        return None
    except subprocess.TimeoutExpired:
        return None

    if result.returncode != 0:
        return None

    if not result.stdout.strip():
        return None

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None

    tasks = data if isinstance(data, list) else data.get("tasks", data.get("items", [data]))
    current = Path.cwd().resolve()
    tasks = [task for task in tasks if _workspace(task) == current]
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


def _workspace(task: dict[str, Any]) -> Path | None:
    value = task.get("workspace_path") or task.get("workspace")
    if not value:
        return None
    if isinstance(value, str) and value.startswith("dir:"):
        value = value[4:]
    try:
        return Path(value).expanduser().resolve()
    except (OSError, TypeError, ValueError):
        return None


def _route(tasks: list[dict[str, Any]], explicit_id: str | None = None) -> dict[str, Any]:
    current = Path.cwd().resolve()
    matching = [task for task in tasks if _workspace(task) == current]
    if explicit_id:
        selected = next((task for task in tasks if task.get("id") == explicit_id), None)
        if selected is None:
            return {"route": "no_card", "action": "work_shaping"}
        if _workspace(selected) != current:
            return {"route": "workspace_mismatch", "action": "block"}
        matching = [selected]
    if not matching:
        return {"route": "no_card", "action": "work_shaping"}
    if len(matching) > 1 and not explicit_id:
        candidates = sorted(
            ({"id": task.get("id"), "title": task.get("title", "?")} for task in matching),
            key=lambda candidate: (str(candidate["id"]), str(candidate["title"])),
        )
        return {"route": "needs_card_selection", "action": "orchestrator", "candidates": candidates}
    selected = matching[0]
    status = selected.get("status")
    # Ginflow logical states map to Hermes Kanban persistence states.
    # Hermes has no `next`/`in_progress`: todo/ready is next; running is active.
    status = {"todo": "next", "ready": "next", "running": "in_progress"}.get(str(status), status)
    if status == "blocked":
        return {
            "route": "blocked_card", "action": "orchestrator", "id": selected.get("id"),
            "blocker_metadata": selected.get("blocker_metadata") or selected.get("metadata", {}).get("blocker")
            if isinstance(selected.get("metadata"), dict) else None,
        }
    if status == "next":
        return {"route": "validate_card_docs", "action": "validate_docs", "id": selected.get("id")}
    if status == "in_progress":
        return {"route": "ready_to_start", "action": "execute", "id": selected.get("id")}
    if status in {"done", "cancelled", "archived"}:
        return {"route": "terminal_card", "action": "block", "id": selected.get("id")}
    return {"route": "invalid_status", "action": "block", "id": selected.get("id")}


def _routing_context(**kwargs: Any) -> dict[str, str] | str | None:
    """Inject deterministic workspace/card routing context when ginflow is active."""
    if not _ginflow_loaded():
        return None

    tasks = _load_tasks()
    explicit_id = os.environ.get("HERMES_KANBAN_TASK") or None
    route = _route(tasks, explicit_id)
    route_name = route["route"]
    candidates = route.get("candidates", [])
    candidate_ids = [item["id"] if isinstance(item, dict) else item for item in candidates]
    current = Path.cwd().resolve()
    if route_name == "no_card":
        route_name = "no_cards_for_workspace"
    if route_name == "invalid_status":
        route_name = "validation_failed"
    action = route.get("action", "block")
    context = (
        f"[ginflow-gate routing: route={route_name}; workspace={current}; "
        f"mutation_allowed={action == 'execute'}; "
        f"task={route.get('id', explicit_id or 'none')}; "
        f"candidates={','.join(candidate_ids) if candidate_ids else 'none'}. "
    )
    if route_name == "no_cards_for_workspace":
        context += "Report workspace to orchestrator; route to work shaping, shape work, or create a card. Load and follow the `plan` skill before creating a plan."
    elif route_name == "needs_card_selection":
        details = "; ".join(f"{item['id']}: {item['title']}" for item in candidates)
        context += f"Report candidates to orchestrator; ask orchestrator to select one card from candidates ({details}); Do not select or implement."
    elif route_name == "blocked_card":
        metadata = route.get("blocker_metadata")
        context += "Report blocker to orchestrator; do not implement."
        if metadata:
            context += f" Blocker metadata: {json.dumps(metadata, sort_keys=True)}."
    elif route_name == "validate_card_docs":
        selected = next((task for task in tasks if task.get("id") == route.get("id")), None)
        if selected:
            card = _normalize_task(selected)
            validation = startup_gate(card, current, current)
            route_name = validation["route"]
            context = context.replace("route=validate_card_docs", f"route={route_name}")
            context += " Validate linked docs before next-to-in_progress transition."
        else:
            context += " Validate linked docs before next-to-in_progress transition."
    elif route_name == "ready_to_start":
        context += "Resume implementation only within validated workspace and scope."
    else:
        context += "Do not implement; report route to orchestrator."
    return {"context": context + "]"}


def _normalize_task(task: dict[str, Any]) -> dict[str, Any]:
    """Adapt live task fields for the shared Ginflow startup validator."""
    body = task.get("body", "")
    fields = _core.parse_card_body(body)
    workspace = task.get("workspace") or task.get("workspace_path") or ""
    if task.get("workspace_kind") and task.get("workspace_path"):
        workspace = f"{task['workspace_kind']}:{task['workspace_path']}"
    return {
        "id": task.get("id"), "title": task.get("title"),
        "objective": fields["objective"], "scope": fields["scope"],
        "acceptance": fields["acceptance"], "links": fields["links"],
        "workspace": workspace, "status": task.get("status"),
        "assignee": task.get("assignee"),
    }


def _load_tasks() -> list[dict[str, Any]]:
    """Load board tasks as dictionaries; return empty on unavailable board."""
    try:
        result = subprocess.run(
            ["hermes", "kanban", "list", "--json"],
            text=True,
            capture_output=True,
            timeout=15,
        )
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        return []
    if result.returncode != 0 or not result.stdout.strip():
        return []
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []
    tasks = data if isinstance(data, list) else data.get("tasks", data.get("items", [data]))
    return [task for task in tasks if isinstance(task, dict)]


def register(ctx) -> None:
    ctx.register_hook("pre_llm_call", _routing_context)
