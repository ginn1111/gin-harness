---
status: completed
size: M
scope: ginflow project-local Kanban context initialization
owner: ginb
---

# Design — Project-local Ginflow context initialization

## Decision

Ginflow will use `.ginflow.yaml` at the current project repository root as the only project-local canonical Kanban context file. It will not read, migrate, or write `.hermes/ginflow.yaml`, and it will not add a `ginflow` CLI.

The initialization event is the first `/ginflow` skill invocation in a project where `.ginflow.yaml` does not exist. The skill resolves the current working directory to an absolute path, discovers the current/default Kanban board, and asks the user to either use that board or create a new board. A new board requires a non-empty user-provided board name. The config is persisted only after a complete context has been resolved and, when requested, board creation has succeeded.

## Config schema

```yaml
version: 1
ginflow:
  board: <Kanban board slug>
  workspace: /absolute/path/to/project
```

`workspace` is the resolved project root. `board` is the selected Kanban board slug. Writes use a temporary file followed by an atomic replace and never create a partial config.

## Resolution and interaction

For an existing config, board precedence is:

1. explicit runtime/API override;
2. `HERMES_KANBAN_BOARD`;
3. `ginflow.board` in `.ginflow.yaml`;
4. Hermes's current/default board.

Workspace mismatch is always checked before using the board. An explicit board override cannot hide a config that belongs to another workspace.

For a missing config, `/ginflow` displays the resolved workspace and current/default board, then asks:

- use the current/default board; or
- create a new board.

If the user chooses a new board, the skill asks for the board name and rejects empty or whitespace-only input. The native Kanban operation creates the board first. Only a successful result permits writing `.ginflow.yaml`. If no current board can be resolved, or board creation fails, the skill asks for clarification and leaves no config behind.

An existing valid config is read without being overwritten during ordinary skill loading. A malformed config, missing required values, invalid workspace, or workspace mismatch fails closed and asks the user to repair or explicitly override it. The skill never silently switches repository, board, or config location.

## Data flow

1. `/ginflow` starts and resolves the current project root.
2. The project root is checked for `.ginflow.yaml`.
3. If present, YAML is parsed and the version, board, workspace, and workspace match are validated.
4. If absent, the skill resolves the current/default board and presents the two-way user choice.
5. The selected board is either accepted or created through native Hermes Kanban operations.
6. The complete `{version, ginflow.board, ginflow.workspace}` payload is written atomically to `<repo>/.ginflow.yaml`.
7. Subsequent verification and routing read this file, applying only explicit runtime overrides allowed by the precedence rules.

No Hermes global configuration is changed. `.hermes/ginflow.yaml` is ignored even if it exists.

## Error handling

The flow fails closed for an invalid current directory, malformed YAML, unsupported/missing schema fields, invalid or mismatched workspace, unavailable current board, empty new-board name, failed board creation, or failed config write. Missing config is expected only during first-use initialization; it is not permission to run Kanban work without completing initialization.

Errors should identify the project-local path and the corrective action without exposing credentials. Board or workspace mismatch must be reported as a mismatch, not repaired implicitly.

## Testing

Tests should cover:

- first `/ginflow` load with no config;
- current/default board selection and exact versioned config output;
- new-board selection requiring a non-empty name;
- successful native board creation before persistence;
- board-creation failure and unresolved-board paths leaving no partial config;
- valid config loading without overwrite;
- malformed, incomplete, and workspace-mismatched configs failing closed;
- explicit board and environment precedence;
- explicit board not bypassing workspace mismatch;
- no reads or writes of `.hermes/ginflow.yaml`;
- verification/routing using only the project-root config;
- atomic persistence and resolved absolute workspace paths.

Run the project checks after implementation:

```bash
make lint
make test
```

## Scope boundaries

This design does not add a new CLI, modify Hermes global config, migrate legacy config files, select a board silently, switch workspaces, or change profile identity and credentials. The implementation is scoped to the Ginflow skill, project-context library, routing/verification adapters, and deterministic tests.

**Status: completed** — implemented with project-local context validation, fail-closed first-use initialization, native board-creation ordering, and deterministic verification.
