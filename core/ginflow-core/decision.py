"""Deterministic Decision readiness, projection, and notification contracts."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from hashlib import sha256
import json
import re
from typing import Any

_SECRET = re.compile(r"(secret|token|cookie|prompt|transcript|raw_log|session_storage)", re.I)


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _required(record: Mapping[str, Any], fields: Sequence[str]) -> None:
    missing = [field for field in fields if not _text(record.get(field))]
    if missing:
        raise ValueError("missing provenance: " + ", ".join(missing))


def _validate_evidence(record: Mapping[str, Any]) -> None:
    evidence = record.get("evidence")
    if not isinstance(evidence, Sequence) or isinstance(evidence, (str, bytes)) or not evidence:
        raise ValueError("evidence is required")
    ids: set[str] = set()
    for item in evidence:
        if not isinstance(item, Mapping) or not all(_text(item.get(field)) for field in ("id", "kind", "producer", "commit", "source", "result", "timestamp", "digest")):
            raise ValueError("evidence has incomplete provenance")
        if item["id"] in ids:
            raise ValueError("duplicate evidence id")
        ids.add(item["id"])
    for claim in record.get("claims", []):
        if not isinstance(claim, Mapping) or not _text(claim.get("text")) or not claim.get("evidence_ids") or not set(claim["evidence_ids"]).issubset(ids):
            raise ValueError("unsupported claim must reference evidence")


def decision_ready(record: Mapping[str, Any]) -> dict[str, Any]:
    """Validate terminal Integration output and return material readiness."""
    if not isinstance(record, Mapping):
        raise ValueError("decision record must be a mapping")
    _required(record, ("initiative_key", "batch_key", "review_key", "baseline_commit", "result_commit", "target_commit"))
    if record.get("result_clean") is not True:
        raise ValueError("mutable result state blocks Decision")
    if record["baseline_commit"] == record["result_commit"]:
        raise ValueError("result commit must differ from baseline")
    tickets = record.get("tickets")
    if not isinstance(tickets, Sequence) or isinstance(tickets, (str, bytes)) or not tickets:
        raise ValueError("tickets are required")
    for ticket in tickets:
        if ticket.get("state") not in {"completed", "failed", "blocked"}:
            raise ValueError("running ticket blocks Decision")
    paths = record.get("changed_paths")
    if not isinstance(paths, Sequence) or any(not isinstance(path, Mapping) or not _text(path.get("path")) or not _text(path.get("change_group")) for path in paths):
        raise ValueError("unassigned changed path blocks Decision")
    verification = record.get("verification")
    if not isinstance(verification, Mapping) or verification.get("commit") != record["result_commit"]:
        raise ValueError("verification must bind result commit")
    _validate_evidence(record)
    return {"outcome": "decision_ready", "initiative_key": record["initiative_key"], "batch_key": record["batch_key"], "review_key": record["review_key"], "result_commit": record["result_commit"]}


def _safe_projection(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _safe_projection(item) for key, item in value.items() if not _SECRET.search(str(key))}
    if isinstance(value, list):
        return [_safe_projection(item) for item in value]
    return value


def build_projection(record: Mapping[str, Any], *, summary: str) -> dict[str, Any]:
    """Build bounded redacted projection ordered for progressive disclosure."""
    decision_ready(record)
    if not _text(summary) or len(summary) > 1000:
        raise ValueError("summary must be bounded")
    projection = {
        "schema": "decision_projection/v1",
        "decision_required": "human disposition required",
        "executive_context": {"initiative_key": record["initiative_key"], "summary": summary},
        "behavior_delta": deepcopy(list(record["changed_paths"])),
        "change_groups": sorted({path["change_group"] for path in record["changed_paths"]}),
        "ticket_coverage": deepcopy(list(record["tickets"])),
        "verification": deepcopy(dict(record["verification"])),
        "risks_findings": deepcopy(list(record.get("findings", []))),
        "choices": ["accept", "enhance", "reject", "defer"],
        "exact_commits": {key: record[key] for key in ("baseline_commit", "result_commit", "target_commit")},
    }
    result = _safe_projection(projection)
    encoded = json.dumps(result, sort_keys=True, separators=(",", ":"))
    if len(encoded) > 10000:
        raise ValueError("decision projection exceeds bound")
    return result


def build_notification(record: Mapping[str, Any], *, message: str, outcome: str = "decision_ready") -> dict[str, Any]:
    """Build gateway-ready envelope; transport and retries remain adapter-owned."""
    ready = decision_ready(record)
    if outcome not in {"decision_ready", "decision_blocked"} or not _text(message) or len(message) > 500:
        raise ValueError("invalid notification outcome or message")
    key = f"{record['batch_key']}:{record['review_key']}:{outcome}"
    return {
        "schema": "notification/v1",
        "event_id": sha256(key.encode()).hexdigest(),
        "initiative_key": record["initiative_key"],
        "batch_key": record["batch_key"],
        "review_key": record["review_key"],
        "outcome": outcome,
        "result_commit": ready["result_commit"],
        "message": message,
        "query_key": f"decision:{record['review_key']}",
        "idempotency_key": key,
        "delivery": {"attempts": 0, "acknowledged": False, "replay_key": key},
    }


__all__ = ["build_notification", "build_projection", "decision_ready"]
