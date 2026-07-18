# Blank project checklist

If user starts in blank project, inspect local context first.

## Check for
- `AGENTS.md`
- `.hermes.md`
- `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Makefile`, or equivalent
- test/lint/build scripts
- repo structure clues

## If missing
Help user create minimum local setup:

- copy setup repo `templates/AGENTS.md` first when available
- retain its routing line to `ginflow`

- project summary
- install command
- dev/run command
- build command
- test command
- lint/typecheck command
- key directories
- forbidden or sensitive paths
- deploy/release rules if any
- done = exact verification path
- one canonical verification command (`verify.sh`, `make verify`, package script, or equivalent)
- file/git conventions and project-specific completion additions

If executable project files already exist, run baseline verification before implementation. For a truly blank repo, record `baseline unavailable: no implementation yet`, then verify after scaffold.

## Workspace check
If repo behavior looks wrong, compare:
- `pwd`
- `echo $TERMINAL_CWD`

If `TERMINAL_CWD` points at old/setup repo, it can override project cwd for Hermes tools.
For clean target-repo tests:

```bash
env -u TERMINAL_CWD hermes ...
```

## Rule
Do not pretend missing commands are known.
Leave placeholders if needed.
Then route work: investigate / implement / brainstorm.

Completion requires local context plus a documented runnable verification path.
