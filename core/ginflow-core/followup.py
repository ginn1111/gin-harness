"""Immutable routing for human Decision follow-up work."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any

_ROUTES = {"implementation": "Execution", "correction": "Execution", "contract": "Shaping", "behavior": "Shaping", "acceptance": "Shaping", "dependency": "Shaping", "problem": "Discovery", "vocabulary": "Discovery", "goal": "Discovery", "boundary": "Discovery"}


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def route_followup(request: Mapping[str, Any]) -> dict[str, Any]:
    """Route one bounded follow-up without reopening prior records."""
    required = ("delta_class", "initiative_key", "review_key", "delta", "scope", "exclusions", "acceptance", "verification", "risk", "ticket_mapping")
    missing = [field for field in required if field not in request or (field in {"delta_class", "initiative_key", "review_key", "delta", "risk"} and not _text(request[field])) or (field not in {"delta_class", "initiative_key", "review_key", "delta", "risk"} and not isinstance(request[field], Sequence))]
    if missing:
        raise ValueError("follow-up packet missing: " + ", ".join(missing))
    route = _ROUTES.get(request["delta_class"])
    if not route:
        raise ValueError("unsupported follow-up delta class")
    packet = deepcopy(dict(request))
    packet["schema"] = "execution_packet/v1"
    packet["batch_attempt"] = 2 if route == "Execution" else None
    packet["immutable"] = True
    return {"route": route, "packet": packet, "policy_proposals": []}


__all__ = ["route_followup"]
