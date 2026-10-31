---
status: draft
scope:
  - plugins/with-chatgpt/
  - INSTALL.md
  - docs/c2c-architecture.html
owner: default
---

# CHAT-1 — Plain conversation with ChatGPT

## Objective

Hermes sends ordinary messages to ChatGPT and reads replies through external
`terminal-browser`. ChatGPT retains authenticated, read-only workspace MCP access
through the existing C2C bridge and ngrok. The user requested removal of C2C
message formats and orchestration, and confirmed retaining workspace access.

## Behavior

- Reuse the saved conversation and workspace connector. A new workspace uses an
  ordinary chat; existing Project bindings remain usable.
- Exchange plain text. No message envelopes, task IDs, iterations, phases,
  checkpoints, execution records, or prescribed plan/review cycle.
- Keep explicit session activation, setup/doctor/pair/stop, and conversation URL
  storage. Hook supplies only a short plain-chat reminder when enabled.
- Remove execution-record MCP tools and CLI commands. Keep workspace information,
  file/image reads, search, Git status, and Git diff.
- Preserve existing local state on disk. Ignore historical protocol metadata;
  retain it when updating conversation metadata without using it for decisions.
- Preserve loopback binding, OAuth/PKCE, pairing, bearer authorization, workspace
  binding, sensitive-path filtering, and read-only remote access.
- Keep browser interaction explicit. User instructions to send a message authorize
  that message; credentials and workspace contents are not pasted into chat.

## Acceptance

1. Active instructions and hook support ordinary conversation without protocol
   or orchestration requirements.
2. Session storage reuses existing chat URLs in both chat and Project modes and
   preserves historical local fields without exposing them as workflow state.
3. CLI and MCP expose no execution-record or checkpoint operations.
4. Security and workspace MCP tests pass alongside plugin checks, runtime tests,
   typecheck/build, and `make lint && make test`.

## Boundaries

No profile installation, live pairing, browser messages, credential changes,
runtime-state cleanup, or unrelated Ginflow changes. No new dependencies.
