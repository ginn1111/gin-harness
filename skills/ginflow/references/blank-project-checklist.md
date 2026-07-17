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

## Rule
Do not pretend missing commands are known.
Leave placeholders if needed.
Then route work: investigate / implement / brainstorm.
