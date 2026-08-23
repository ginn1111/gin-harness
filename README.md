# Gin-harness

Gin-harness is a standalone artifact repository for safer agent work. It provides the shared **Ginflow** workflow, reusable routing and validation primitives, an optional `ginflow-gate` adapter, target-project starter context, and deterministic integration checks.

It is not a product application. Target repositories own product code, local rules, tests, and canonical product verification. Runtime-specific integrations, including Hermes skill/plugin loading, remain optional consumers of these artifacts.

## Table of contents

- [Why it exists](#why-it-exists)
- [Installation](#installation)
- [Usage](#usage)
- [Architecture](#architecture)
- [Further reading](#further-reading)
- [Project rules](#project-rules)

## Why it exists

A raw prompt does not reliably establish the target workspace, requirements, root cause, work size, risk, verification command, or completion authority.

Ginflow adds a fail-closed workflow around Hermes:

- **Clarification** keeps unresolved work read-only until the missing facts are known.
- **Direct Work** allows affirmatively eligible, localized XS/S changes without a card.
- **Governed Work** uses a complete Kanban card for larger, risky, coordinated, or artifact-requiring work.
- **Completion gates** validate card fields, verification evidence, linked artifacts, baseline commits, and drift.

## Installation

Read [`INSTALL.md`](INSTALL.md) for prerequisites, validation, artifact consumption, optional Hermes integration, and troubleshooting.

For this repository, run:

```bash
make lint
make test
```

The repository does not require Hermes, a Hermes profile, or profile configuration. Consume optional Hermes adapters separately when a runtime needs them.

## Usage

1. Work from the real target repository, not the setup repository.
2. Read the target project's `AGENTS.md` or `.hermes.md`.
3. Inspect Git state and Kanban progress before mutable work.
4. Route the request to Clarification, Direct Work, or Governed Work.
5. For Governed Work, use the selected card's workspace, scope, acceptance, assignee, and linked artifacts.
6. Run the target project's canonical verification command.
7. Complete governed work with the native `kanban_complete` tool so `ginflow-gate` can validate the result.

The setup checks and target-project checks are separate evidence. Ginflow does not replace the target project's canonical verification.

## Architecture

```text
User intent
    │
    ▼
Hermes runtime ── loads ──> Ginflow skill
    │                         │
    │                         ├─ workflow vocabulary
    │                         └─ output contract
    │
    └─ invokes ginflow-gate ──> routing context and completion gate

Ginflow core ── reusable routing and validation primitives

Target project ── product code, local rules, tests, canonical verification
```

The skill defines the workflow contract. Ginflow core provides reusable primitives. The optional plugin supplies bounded routing context and completion enforcement. The consuming runtime owns execution and lifecycle details. The target project owns product behavior and its canonical verification.

## Further reading

- [Installation guide](INSTALL.md)
- [Architecture overview](docs/architecture/README.md)
- [Editable Draw.io architecture](docs/architecture/gin-harness-system.drawio)
- [Ginflow flow](docs/architecture/ginflow-flow.md)
- [Ginflow workflow skill](skills/ginflow/SKILL.md)
- [`ginflow-gate` plugin](plugins/ginflow-gate/)
- [Reusable Ginflow core](core/ginflow-core/)
- [Target-project setup template](templates/AGENTS.md)

## Project rules

See [`AGENTS.md`](AGENTS.md) for repository boundaries, verification order, generated-file handling, and completion rules.

_Gin-harness documents the workflow around execution; it does not replace Hermes Agent or the target project._
