# Target Hermes architecture

## System shape

```text
                 ChatGPT Web
             ORCHESTRATOR
                 │          ▲
             MCP │          │ Control
                 ▼          │
            C2C Bridge      │
                 │          │
            read-only       │
                 ▼          │
             Workspace      │
                 ▲          │
                 │          │
        edit / shell / git  │
                 │          │
              Hermes ───────┘
              EXECUTOR
```

Only executor changes.

```text
ChatGPT owns decisions.
Hermes owns execution.
C2C owns observation/access.
```

Workspace remains source of truth.

## Responsibility boundary

### ChatGPT: orchestrator, planner, reviewer

- Interpret task goals.
- Inspect current workspace through read-only MCP.
- Decide what should happen next.
- Return concrete `PLAN` messages.
- Review current code, diff, and recorded execution evidence independently.
- Return another `PLAN`, `DONE`, or `BLOCKED`.

ChatGPT receives no shell, file-write, package-install, commit, or other mutation capability from C2C.

### Hermes: executor

- Detect workspace and C2C checkout.
- Start or reuse bridge.
- Establish or reuse persistent ChatGPT browser session.
- Send and parse C2C control messages.
- Decide how to carry out approved plan safely using Hermes file, terminal, test, and git tools.
- Record execution metadata and sanitized output.
- Persist checkpoint transitions.
- Continue until ChatGPT returns `DONE`; do not treat `EXECUTED` as completion.

Hermes chooses execution mechanics within approved plan. Hermes must not silently expand scope.

### C2C: observation and access

- Preserve read-only MCP tools and security boundary.
- Preserve OAuth, pairing, tunnel, process, execution-record, and workspace behavior.
- Preserve C2C wire states and state storage in V1.
- Remain independent of Hermes coding internals.

### Workspace: truth

- Holds code and git state.
- Supplies review evidence to ChatGPT through MCP.
- Receives mutations only from Hermes.

## Control loop

```text
User goal
  → Hermes sends INIT
  → ChatGPT inspects workspace through MCP
  → ChatGPT sends PLAN
  → Hermes checkpoints PLAN_RECEIVED / EXECUTING
  → Hermes edits and verifies
  → Hermes records execution
  → Hermes checkpoints EXECUTED_LOCAL
  → Hermes sends EXECUTED
  → Hermes checkpoints EXECUTED_SENT
  → ChatGPT reviews through MCP
  → PLAN | DONE | BLOCKED
```

Control messages remain under 1 KiB and contain no source code, diffs, or large logs. ChatGPT reads those through MCP.

## Integration strategy

1. Rewrite Skill procedures first.
2. Keep C2C protocol and bridge unchanged unless evidence proves required adaptation.
3. Use Hermes browser tools and persistent browser session from Skill procedures before adding TypeScript browser APIs.
4. Remove Codex sandbox mutation from normal Hermes setup because Hermes terminal/file tools are not governed by Codex `sandbox_workspace_write`.
5. Keep `c2c`, `[C2C]`, `.c2cignore`, state layout, and legacy connector labels where compatibility requires them.
6. Write `executor="hermes"` in new execution records while continuing to read older records with missing/Codex executor values.

## Security invariants

- MCP stays read-only.
- Bridge stays loopback-only; tunnel remains OAuth-protected.
- Tokens stay workspace-bound.
- Sensitive-file and path-containment policies remain unchanged.
- Workspace content remains untrusted.
- Browser control transfers protocol metadata only.
- Hermes does not paste files, diffs, logs, or test output into ChatGPT messages.

## Architecture decision

No new coding harness or generic executor abstraction. Hermes already supplies execution capabilities. Migration replaces Codex-specific Skill instructions and setup assumptions, preserving bridge design.
