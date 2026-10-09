# Upstream architecture

## System shape

```text
                 ChatGPT Web
          Reason / Plan / Review
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
               Codex ───────┘
```

Upstream separates two planes:

- **MCP data plane:** ChatGPT reads bounded workspace, git, and execution-record data through C2C.
- **Control plane:** Codex types small `[C2C]` state messages into ChatGPT Web through browser automation.

Workspace remains source of truth. Control messages carry state and metadata, never file bodies, diffs, or long logs.

## Responsibilities

### ChatGPT

- Understand request.
- Inspect repository through MCP.
- Produce finite execution plans.
- Review implementation independently through MCP.
- Return another `PLAN`, terminal `DONE`, or `BLOCKED`.

### C2C Bridge

- Expose workspace through ten read-only MCP tools.
- Enforce workspace containment, sensitive-file policy, pagination, and per-tool OAuth scopes.
- Provide OAuth discovery, dynamic client registration, PKCE, token rotation, revocation, and workspace-bound bearer authorization.
- Provide pairing, tunnel lifecycle, bridge process state, and local admin API.
- Persist sanitized execution records and resumable session/checkpoint state.

Concrete assembly lives in `src/bridge/server.ts::startBridge`. `/mcp` is bearer-protected. Admin routes require loopback access and random admin token.

### Codex

- Transport control messages through ChatGPT Web.
- Edit files.
- Run shell commands, tests, builds, and typechecks.
- Use git.
- Execute approved plans.
- Record iteration results through `c2c record`.
- Resume from C2C checkpoints and create `HANDOFF` messages when conversation recovery is needed.

Most executor behavior lives in `skill/SKILL.md`, not bridge runtime.

### Workspace

- Source of truth for code and review.
- Security boundary: one bridge serves one canonical workspace.
- Identity source for workspace-bound runtime, auth, endpoint, tunnel, session, and execution state.

## Read-only enforcement

Read-only behavior is structural, not prompt-only:

1. `src/mcp/server.ts::createMcpServer` registers only observation tools:
   `workspace_info`, `list_directory`, `read_file`, `read_image`,
   `search_workspace`, `git_status`, `git_diff`, `test_status`,
   `execution_summary`, and `execution_output`.
2. Every tool declares `readOnlyHint: true`.
3. No write, delete, shell, commit, install, or arbitrary process tool is registered.
4. Workspace paths pass through `Workspace` containment and ignore policy.
5. Git and execution tools only read existing state.
6. OAuth scopes restrict each tool family further.

ChatGPT therefore cannot mutate workspace through C2C even if workspace content contains prompt injection.

## Request flows

### MCP observation

```text
ChatGPT
  → HTTPS tunnel
  → /mcp
  → bearerAuth(workspaceId)
  → fresh stateless MCP server
  → scoped tool handler
  → Workspace containment/sensitive-file policy
  → bounded response
```

### Authorization

```text
/mcp 401
  → protected-resource metadata
  → OAuth server metadata
  → dynamic client registration
  → authorization page + one-time pairing code
  → authorization code + PKCE S256
  → workspace-bound access/refresh tokens
```

### Execution/review loop

```text
Codex sends INIT
  → ChatGPT inspects through MCP
  → ChatGPT sends PLAN
  → Codex edits/runs/tests
  → Codex records sanitized metadata
  → Codex sends EXECUTED
  → ChatGPT inspects current workspace through MCP
  → PLAN | DONE | BLOCKED
```

### Resume

`src/session/state.ts` stores local checkpoint states separately from wire states. Codex reads latest durable state and either resumes existing chat or sends `HANDOFF` to replacement conversation. No `RESUME` wire state exists.

## Preserve candidates

Executor-neutral infrastructure:

- `src/mcp/`
- `src/auth/`
- `src/pairing/`
- `src/workspace/`
- `src/tunnel/`
- `src/execution/`
- `src/bridge/`
- `src/process/`
- most of `src/session/`

Primary executor coupling exists in `skill/SKILL.md`, Codex sandbox configuration, CLI setup/doctor calls, and user-facing branding.
