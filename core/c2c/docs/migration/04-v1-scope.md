# V1 scope

## Proof target

V1 proves one bounded loop:

```text
ChatGPT
   ↓ PLAN
Hermes
   ↓ execution
Workspace
   ↓ MCP inspection
ChatGPT
   ↓ review
PLAN or DONE
```

Required behavior:

- Hermes starts or reuses C2C bridge.
- ChatGPT reads correct workspace through MCP.
- Hermes sends `INIT` and receives `PLAN` without copy/paste.
- Hermes executes plan with its own tools.
- Hermes records execution and sends `EXECUTED` metadata only.
- ChatGPT independently reviews workspace through MCP.
- Additional plan iterations work.
- Only `DONE` completes task.
- `BLOCKED`, resume, and `HANDOFF` preserve protocol semantics.

## Hard non-goals

- No writable MCP.
- No ChatGPT shell access.
- No ChatGPT file editing.
- No multi-worker Hermes.
- No Kanban integration.
- No Hermes sub-agents.
- No protocol redesign.
- No distributed execution.
- No large executor abstraction.
- No unnecessary C2C to H2C rename.
- No Hermes Agent source modification.
- No broad browser framework.
- No state-directory rename without explicit compatibility migration.
- No connector rename that strands existing ChatGPT configuration.

## V1 names retained

Keep unless later evidence requires migration:

- `c2c` CLI
- `[C2C]` control-message prefix
- `.c2c.json`
- `.c2cignore`
- `C2C_*` environment variables
- C2C state paths
- stored legacy connector names

These identify bridge/protocol compatibility, not executor ownership.

## Acceptance boundary

V1 is not complete from unit tests alone. Live acceptance needs:

- persistent authenticated ChatGPT browser session;
- connected MCP connector;
- real `INIT → PLAN → EXECUTED → DONE` flow;
- second-plan iteration;
- restart/resume and conversation handoff;
- Linux and macOS manual matrix.

Current development host lacks `cloudflared`; tunnel acceptance remains blocked until dependency is installed.
