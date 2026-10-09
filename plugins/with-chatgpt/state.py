"""Profile/session activation state for Hermes with ChatGPT."""

from __future__ import annotations

from typing import Any

_STATE_KEY = "sessions"
_MAX_SESSIONS = 32
_MAX_SESSION_ID = 160


def _valid_session_id(value: object) -> bool:
    return isinstance(value, str) and 0 < len(value.strip()) <= _MAX_SESSION_ID and "\x00" not in value


def _sessions(state: Any) -> dict[str, dict[str, Any]]:
    raw = state.get(_STATE_KEY, {})
    if not isinstance(raw, dict):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for key, value in raw.items():
        if _valid_session_id(key) and isinstance(value, dict):
            result[key] = {"enabled": True}
    return result


def session_enabled(state: Any, session_id: str | None) -> bool:
    return bool(session_id and _sessions(state).get(session_id.strip(), {}).get("enabled"))


def enable_session(state: Any, session_id: str) -> None:
    if not _valid_session_id(session_id):
        raise ValueError("session id is required and must be <= 160 characters")
    sessions = _sessions(state)
    sessions[session_id.strip()] = {"enabled": True}
    while len(sessions) > _MAX_SESSIONS:
        del sessions[next(iter(sessions))]
    state.set(_STATE_KEY, sessions)


def disable_session(state: Any, session_id: str) -> None:
    sessions = _sessions(state)
    sessions.pop(session_id.strip(), None)
    state.set(_STATE_KEY, sessions)


def clear_session(state: Any, session_id: str | None) -> None:
    if session_id:
        disable_session(state, session_id)


def active_session_count(state: Any) -> int:
    return len(_sessions(state))
