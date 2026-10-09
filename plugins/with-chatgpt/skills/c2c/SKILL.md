---
name: c2c
description: Use Hermes with ChatGPT for explicit planning and review while C2C provides authenticated read-only workspace observation.
---

# Hermes with ChatGPT

ChatGPT plans and reviews. Hermes executes. C2C provides authenticated, read-only workspace observation.

Collaboration is disabled by default. Enable it explicitly for current Hermes session with `hermes with-chatgpt enable --session-id <id>`. Disable affects only current session. New sessions start disabled.

## Rules

1. Never paste source files, diffs, logs, credentials, cookies, browser storage, pairing codes, access tokens, refresh tokens, or bridge admin tokens into ChatGPT. ChatGPT reads allowed workspace data through read-only MCP.
2. Never grant ChatGPT write, delete, shell, execution, or commit capability. Hermes owns all local mutation and verification.
3. Keep control messages bounded and use C2C protocol state:
   `INIT → PLAN → EXECUTING → EXECUTED → REVIEW → PLAN | DONE | BLOCKED`.
4. Reuse current workspace connector and saved conversation. Never silently create/switch conversations, churn a healthy connector/tunnel, or use another workspace connector.
5. Run `c2c doctor --json` and inspect results before explicit browser work. Unknown bridge state is not stopped; do not start another bridge.
6. Browser interaction remains an explicit workflow through external `terminal-browser`; never run it from `pre_llm_call`.
7. Save resumable checkpoint state before/after browser work. On timeout/interruption, resume from checkpoint instead of discarding state.
8. Require confirmation before consequential browser actions. End automation by clearing browser action indicator.

## Lifecycle

- `INIT`: verify session activation, workspace binding, connector health, and local C2C status.
- `PLAN`: use explicit browser workflow to ask ChatGPT for bounded plan; store checkpoint.
- `EXECUTING`: Hermes implements plan locally, runs canonical tests, and records execution with `executor: hermes`.
- `EXECUTED`: save changed files, tests, and checkpoint. Send only small control message.
- `REVIEW`: ChatGPT reads current workspace through MCP and returns review decision.
- `PLAN`: apply approved follow-up locally, or return to planning when review requests changes.
- `DONE`: record completion and clear checkpoint.
- `BLOCKED`: preserve evidence and next action; run explicit `status`/`doctor` recovery.

## Commands

```text
hermes with-chatgpt setup --json
hermes with-chatgpt doctor --json
hermes with-chatgpt enable --session-id <id>
hermes with-chatgpt disable --session-id <id>
hermes with-chatgpt status --session-id <id> --json
hermes with-chatgpt pair --workspace <path> --json
hermes with-chatgpt stop --workspace <path>
```

`setup` checks Node/build/dependencies and external `terminal-browser`; it does not install browser tooling or mutate Codex configuration. `doctor` is read-only unless explicit `--repair` is passed.
