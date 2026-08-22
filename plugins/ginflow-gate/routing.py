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
CORE_ROUTING = Path(__file__).resolve().parents[2] / "skills/ginflow/lib/routing.py"
_routing_spec = importlib.util.spec_from_file_location("ginflow_routing_core", CORE_ROUTING)
if not _routing_spec or not _routing_spec.loader:
    raise ImportError(f"unable to load Ginflow routing core: {CORE_ROUTING}")
_routing_core = importlib.util.module_from_spec(_routing_spec)
_routing_spec.loader.exec_module(_routing_core)
_route_policy = _routing_core.route
_workspace = _routing_core.workspace

logger = logging.getLogger(__name__)


WORK_MODE_SKILLS = {
    "investigation": "diagnosing-bugs",
    "implementation": "implement",
    "brainstorming": "brainstorming",
    "clarification": "brainstorming",
    "verification": "verification-before-completion",
    "recovery": "executing-plans",
}

WORK_MODES = frozenset(WORK_MODE_SKILLS)
WORK_SIZES = frozenset({"XS", "S", "M", "L", "XL"})

_DEFAULT_OUTPUTS = {
    "spec": "docs/specs/<CARD-ID>.md",
    "plan": "docs/plans/<CARD-ID>.md",
    "wayfinder": "docs/wayfinding/<MAP-ID>.md",
    "handoff": "docs/handoffs/<CARD-ID>.md",
}


def format_work_guidance(
    *,
    work_mode: str,
    work_size: str | None,
    size_rationale: str | None,
    eligibility: str,
    risk_impact: str,
    canonical_verification: str | None = None,
    output_overrides: dict[str, str] | None = None,
) -> str:
    """Render bounded, advisory routing guidance for Hermes.

    This formatter deliberately does not decide eligibility, create records, call
    ``skill_view``, or inspect the selected skill.  Hermes supplies the facts and
    makes the affirmative Direct Work decision.
    """
    mode = work_mode if work_mode in WORK_MODES else "clarification"
    skill = WORK_MODE_SKILLS[mode]
    outputs = dict(_DEFAULT_OUTPUTS)
    if output_overrides:
        outputs.update({key: value for key, value in output_overrides.items() if key in outputs})

    if eligibility == "eligible" and work_size in {"XS", "S"} and risk_impact == "none":
        route = "Direct Work"
        route_id = "direct-no-card"
        output = (
            "Route: direct-no-card (Direct Work). Output: Delivery Change + conversation result; "
            "no Kanban Card, Links field, Governance Artifact, or replacement execution record."
        )
    elif eligibility == "unknown" or work_size not in WORK_SIZES or risk_impact == "unknown":
        route = "Clarification"
        route_id = "clarification"
        output = (
            "Route: Clarification. Permit conversation-led brainstorming or read-only investigation "
            "only; no repository mutation, implementation, Kanban Card, working note, or Governance Artifact."
        )
    else:
        route = "Governed Work"
        route_id = "governed"
        output = (
            "Route: Governed Work. Start and validate a build-ready Kanban Card; use conditional "
            f"Spec/Plan outputs ({outputs['spec']}; {outputs['plan']}) when behavior, contract, ordering, "
            "investigation, risk, rollback, or layered verification requires them. No Brief."
        )

    size_text = work_size or "unknown"
    rationale = size_rationale or "unknown shaping evidence"
    verification = canonical_verification or "unknown canonical verification"
    return (
        f"[ginflow work guidance: work-mode={mode}; route={route_id}; work-size={size_text}; "
        f"size-rationale={rationale}; Risk Impact={risk_impact}; candidate skill: {skill}. "
        f"Before acting, Hermes must call skill_view(name='{skill}'). "
        f"{output} Canonical verification: {verification}. "
        "Direct Work Eligibility must be affirmative: clear requirements and target behavior; "
        "known bug root cause; genuine XS/S; localized reversible scope; no actual Risk Impact; "
        "no Governance Artifact need; known verification; project-local permission; unowned single-worker workspace. "
        "Risky keywords alone are not Risk Impact. The plugin provides guidance only: it never calls skill_view, "
        "creates cards or Governance Artifacts, mutates Kanban, or mechanically authorizes Direct Work. "
        "If scope, clarity, ownership, verification, or impact changes, stop mutation and reclassify before continuing. "
        f"Canonical optional outputs remain {outputs['wayfinder']} and {outputs['handoff']}.]"
    )


def _configured_output_overrides() -> dict[str, str]:
    """Read explicit project-local canonical output overrides, if configured."""
    return {
        key: value
        for key, value in (
            ("spec", os.environ.get("GINFLOW_OUTPUT_SPEC", "")),
            ("plan", os.environ.get("GINFLOW_OUTPUT_PLAN", "")),
            ("wayfinder", os.environ.get("GINFLOW_OUTPUT_WAYFINDER", "")),
            ("handoff", os.environ.get("GINFLOW_OUTPUT_HANDOFF", "")),
        )
        if value
    }


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


def _route(tasks: list[dict[str, Any]], explicit_id: str | None = None) -> dict[str, Any]:
    """Compatibility adapter: inject Hermes cwd into core policy."""
    return _route_policy(tasks, Path.cwd(), explicit_id)


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
        context += (
            "Report workspace to orchestrator; no Kanban card exists for workspace. "
            "Choose work mode: investigation when cause is unclear, implementation when "
            "requirements are clear, or brainstorming when requirements are unclear. "
            "Then choose artifact level, shape work, or create a card. Load and follow "
            "the `plan` skill before creating a plan."
        )
        context += " " + format_work_guidance(
            work_mode="clarification",
            work_size=None,
            size_rationale=None,
            eligibility="unknown",
            risk_impact="unknown",
            output_overrides=_configured_output_overrides(),
        )
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
