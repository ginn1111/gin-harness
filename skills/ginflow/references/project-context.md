# Canonical project context

The first `/ginflow` skill load initializes `.ginflow.yaml` in the current project root:

First-load initialization is agent-procedural: `/ginflow` invokes the initializer and
collects the board choice. Runtime validation and persistence enforce the contract,
but no runtime hook or CLI silently initializes a project.

```yaml
version: 1
ginflow:
  board: <Kanban board slug>
  workspace: /absolute/path/to/project
```

The resolved workspace is the target directory passed to verification. Board precedence is:

1. explicit runtime/API override;
2. `HERMES_KANBAN_BOARD`;
3. `ginflow.board` in `.ginflow.yaml`;
4. Hermes's active board.

A valid existing config is used by Kanban reads when no override is supplied and is not overwritten during ordinary skill loading. If the file is missing, `/ginflow` asks whether to use the current/default board or create a new board. New-board selection requires a non-empty name and successful native board creation before persistence. Malformed, incomplete, or workspace-mismatched config fails closed and must be repaired or explicitly resolved by the user; it never causes a silent workspace or board switch. Verification reads this file but does not initialize or rewrite it.

Routing distinguishes a missing config from an invalid config. Both are mutation
blockers: missing context directs the agent to run `/ginflow`, while invalid context
directs it to repair `.ginflow.yaml`. A valid context with no cards for its workspace
is reported as a normal no-card work-shaping route.
