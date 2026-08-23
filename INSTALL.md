# Ginflow artifact repository

Run commands from the repository root.

## Prerequisites

- Python 3
- POSIX shell
- Make
- Git

Optional:

- CodeGraph for workspace navigation and health reporting
- Hermes Agent if you want to consume the optional `skills/ginflow` skill or `plugins/ginflow-gate` adapter

The repository does not require a Hermes installation, Hermes profile, profile directory, profile manifest, or profile configuration.

## Validate the repository

```bash
make lint
make test
make verify
```

`make test` runs the standalone core, artifact-guidance, Kanban-harness, plugin, recovery, and installation-independent guidance checks. `make verify` runs the Ginflow harness without requiring a target workspace or Hermes profile.

## Consume the artifacts

Use the repository directories directly or copy the required artifacts into another project or runtime:

- `core/ginflow-core/` — reusable routing and validation primitives
- `templates/` — target-project starter context and artifact templates
- `skills/ginflow/` — optional Hermes-compatible workflow skill
- `plugins/ginflow-gate/` — optional Hermes-compatible completion gate
- `skills/ginflow/scripts/` — portable validation and test helpers

For a target project, copy `templates/AGENTS.md` into the target repository and adapt its local commands, boundaries, and canonical verification path.

## Optional Hermes integration

Hermes integration is deliberately outside this repository's runtime boundary. Install or configure Hermes using the official Hermes documentation, then consume the optional skill and plugin according to that runtime's integration mechanism.

This repository does not:

- discover or select Hermes profiles;
- mutate profile configuration;
- install or uninstall profile integrations;
- manage profile identity, secrets, sessions, memories, cron, or provider settings; or
- require Hermes to run its core validation suite.

## Target-project workflow

Do not implement product work in this repository. Agents should use the Ginflow workflow against the real target repository, with the target project's local rules and canonical verification command.

The target project owns:

- product code and tests;
- local `AGENTS.md` / `.hermes.md` rules;
- Kanban-linked Spec, Plan, ADR, and Handoff artifacts; and
- product verification and delivery decisions.

The Ginflow skill and plugin remain optional adapters. They do not replace the target project's own toolchain or verification.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `make` is missing | Install Make from your operating system toolchain |
| Python dependency error | Use Python 3 and rerun `make lint` |
| CodeGraph warning | Install and initialize CodeGraph only if workspace navigation is needed |
| Hermes integration needed | Configure Hermes separately, then consume the optional skill/plugin artifacts |
| Target verification is unknown | Add the canonical command to the target project's local rules |
