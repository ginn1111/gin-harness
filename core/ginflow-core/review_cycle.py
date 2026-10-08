"""Append-only human Review Cycle contract."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from hashlib import sha256
import json
from typing import Any

SEVERITIES = frozenset({"blocking", "high", "medium", "low", "informational"})
DISPOSITIONS = frozenset({"accept", "enhance", "reject", "defer"})
STATES = frozenset({"open", "resolved", "accepted_risk", "not_applicable"})
OUTCOMES = frozenset({"approved_for_mr", "enhancement_requested", "rejected", "resume_execution", "reshape_required", "stopped"})


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _base_errors(record: Mapping[str, Any]) -> list[str]:
    errors = []
    if record.get("schema") != "review_cycle/v1":
        errors.append("schema must be review_cycle/v1")
    for field in ("review_key", "initiative_key", "batch_key"):
        if not _text(record.get(field)):
            errors.append(f"{field} is required")
    actor = record.get("actor")
    if not isinstance(actor, Mapping) or actor.get("claim") != "review:decide" or not all(_text(actor.get(key)) for key in ("id", "profile")):
        errors.append("actor claim is unauthorized")
    if not isinstance(record.get("commits"), Mapping) or not all(_text(record["commits"].get(key)) for key in ("baseline", "result", "target")):
        errors.append("exact commits are required")
    if record.get("aggregate_decision") not in OUTCOMES:
        errors.append("aggregate_decision is unsupported")
    return errors


def validate_review(record: Mapping[str, Any]) -> dict[str, Any]:
    """Validate review data and raise on unsafe decision inputs."""
    if not isinstance(record, Mapping):
        return {"valid": False, "errors": ["review must be a mapping"]}
    errors = _base_errors(record)
    evidence_ids = {item.get("id") for item in record.get("evidence", []) if isinstance(item, Mapping)}
    if not record.get("evidence"):
        errors.append("evidence is required")
    for finding in record.get("findings", []):
        if not isinstance(finding, Mapping) or finding.get("severity") not in SEVERITIES or finding.get("state") not in STATES:
            errors.append("finding is malformed")
            continue
        if finding.get("state") == "accepted_risk" and not _text(finding.get("reason")):
            errors.append("accepted risk reason is required")
        if finding.get("severity") in {"blocking", "high"} and finding.get("state") not in {"resolved", "not_applicable", "accepted_risk"} and record.get("aggregate_decision") == "approved_for_mr":
            errors.append("finding blocks approved_for_mr")
        if not set(finding.get("evidence_ids", [])) <= evidence_ids:
            errors.append("finding references unsupported evidence")
    for disposition in record.get("dispositions", []):
        if not isinstance(disposition, Mapping) or disposition.get("disposition") not in DISPOSITIONS or not _text(disposition.get("change_group")):
            errors.append("disposition is malformed")
    if record.get("aggregate_decision") == "approved_for_mr" and record.get("deviations"):
        errors.append("deviations block approved_for_mr")
    return {"valid": not errors, "errors": errors}


def append_revision(record: Mapping[str, Any], *, actor: Mapping[str, Any]) -> dict[str, Any]:
    """Create one immutable review revision; existing revision cannot be overwritten."""
    candidate = deepcopy(dict(record))
    if candidate.get("immutable") or candidate.get("revision_digest") or candidate.get("revision") != 1:
        raise ValueError("append requires a new review revision")
    if dict(actor) != dict(candidate.get("actor", {})):
        raise ValueError("review actor mismatch")
    result = validate_review(candidate)
    if not result["valid"]:
        raise ValueError("invalid review: " + "; ".join(result["errors"]))
    canonical = json.dumps(candidate, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    candidate["revision_digest"] = sha256(canonical).hexdigest()
    candidate["immutable"] = True
    return candidate


__all__ = ["append_revision", "validate_review"]
