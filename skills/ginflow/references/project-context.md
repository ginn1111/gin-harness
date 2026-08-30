# Canonical project context

The first `/ginflow` skill load initializes `.ginflow.yaml` in the current project root:

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
