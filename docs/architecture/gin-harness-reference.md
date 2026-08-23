# Gin-harness reference architecture

This document is an evidence-based companion to the editable Draw.io diagrams. It explains the current repository implementation and records gaps or external boundaries explicitly.

## What this repository is

Gin-harness is a standalone artifact repository for agent work governance. It is not a product application and it does not own target-project business logic. Its purpose is to make ambiguous, risky, or multi-step work explicit enough to route, execute, verify, and complete without silently bypassing scope or evidence boundaries.

The repository addresses a recurring failure mode: a raw prompt does not by itself establish the target workspace, requirements, root cause, work size, risk, canonical verification, or completion authority. Ginflow adds a vocabulary and validation path around Hermes so unresolved facts lead to Clarification, eligible small work can remain Direct Work, and larger or risky work uses a Kanban card and conditional governance artifacts.

## Runtime and ownership map

| Layer | Current responsibility | Evidence | Authority boundary |
|---|---|---|---|
| Hermes Agent | Profile/runtime lifecycle, skill loading, tools, Kanban, and execution | `skills/ginflow/SKILL.md` (core split and startup) | External runtime; this repo documents integration contracts |
| Ginflow skill | Workflow vocabulary, route/output rules, startup/close/restart guidance, artifact layout | `skills/ginflow/SKILL.md` | Shared procedural guidance loaded by Hermes via `skill_view` |
| Ginflow core | Reusable routing/validation primitives and structured workflow model | `core/ginflow-core/` | Library code; target projects do not own its implementation |
| `ginflow-gate` plugin | Hermes integration hooks, routing context, completion validation, feedback/recovery helpers | `plugins/ginflow-gate/plugin.yaml`, `plugins/ginflow-gate/*.py` | Gate/context provider; not a semantic classifier or replacement runtime |
| Kanban card | Durable governed-work assignment: objective, scope, acceptance, workspace, assignee, status, links, progress | `skills/ginflow/SKILL.md`; `plugins/ginflow-gate/` | Hermes Kanban is lifecycle authority |
| Target project | Product code, local rules, tests, and canonical verification | `AGENTS.md` contract; `skills/ginflow/SKILL.md` | Target repository owns product delivery |
| Repository verification | Standalone artifact lint/test and harness health | `Makefile`, `make verify` | Proves repository health, not target product behavior |
| Target verification | Product-native command selected by target repository | `skills/ginflow/SKILL.md` completion rules | Required evidence for the target change |

## Current user flow

1. **Startup** — confirm the real target workspace and read local `AGENTS.md`/`.hermes.md`.
2. **Route selection** — Hermes evaluates work mode, work size, risk impact, clarity, ownership, and canonical verification with Ginflow guidance.
3. **Clarification** — unresolved requirements, target, cause, size, risk, ownership, artifact need, or verification remain conversation-led and read-only.
4. **Direct Work** — only affirmatively eligible XS/S work may proceed without a card or governance artifact. It must be localized, reversible, low-risk, project-permitted, and verifiable.
5. **Governed Work** — M/L/XL, risky, or artifact-requiring work starts from a complete Kanban card. A Spec is conditional on behavior/contract drift; a Plan is conditional on ordering, investigation, rollback, coordination, or layered verification.
6. **Execution and verification** — the worker changes only the selected workspace and runs the target project's canonical checks. Setup checks remain separate evidence.
7. **Completion** — the native `kanban_complete` tool and `ginflow-gate` validate required fields, linked artifact state, verification metadata, baseline commit, and drift before the card becomes done.

The detailed branch model is in [`ginflow-flow.md`](./ginflow-flow.md), and the routing vocabulary is in [`../../skills/ginflow/SKILL.md`](../../skills/ginflow/SKILL.md).

## Dependency inventory

### Repository-local dependencies

| Dependency | Role | Evidence | Version/status |
|---|---|---|---|
| Python standard library | XML checks, scripts, core/plugin implementation and tests | `core/ginflow-core/*.py`, `plugins/ginflow-gate/*.py`, `skills/ginflow/scripts/*.py` | No package version pinned in this repository |
| POSIX shell utilities | Make targets, verification scripts | `Makefile`, `scripts/*.sh` | Environment-provided; exact versions unknown |
| Make | Canonical repository verification entry point | `Makefile` | Environment-provided; exact version unknown |
| Draw.io XML format | Editable architecture diagrams | `docs/architecture/*.drawio` | File format; editor/runtime version unknown |
| Git | Baseline, diff, and artifact-drift evidence | `Makefile`, `skills/ginflow/SKILL.md` | Environment-provided; exact version unknown |

No committed `pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml`, or requirements file was found during this investigation. Therefore this repository does not provide a pinned third-party dependency inventory; documentation must not invent one.

### External/runtime dependencies

| External dependency | Why it matters | What this repo guarantees | Unknowns / limits |
|---|---|---|---|
| Hermes Agent runtime | Loads skills, invokes tools, owns profiles and Kanban lifecycle | Ginflow instructions and plugin hooks target Hermes contracts | Internal implementation and version are external |
| Hermes native Kanban tools | Durable card state and completion authority | Card shape and native completion boundary are documented | Server/storage details are external |
| Optional Hermes runtime | Consumes the skill/plugin adapters when desired | Adapter contracts are documented; runtime integration is not required here | Runtime installation and configuration are external |
| Optional CodeGraph tooling | Advisory workspace health and code navigation | `validate-harness.py` reports optional health without making it a blocker | Tool installation/connectivity/version are environment-specific |
| Target project's own toolchain | Product implementation and canonical verification | Ginflow requires the target command and reports it separately | Target project controls its dependencies and versions |

## Problems addressed

- **Ambiguous intent:** route to Clarification rather than inventing requirements.
- **Wrong scale:** separate Work Mode, Work Size, and Risk Impact; do not classify by title or raw file count.
- **Workspace collisions:** require a real workspace and one active governed card per mutable workspace.
- **Premature execution:** require a build-ready card for governed work and fail closed on missing fields.
- **Weak completion claims:** require canonical verification and native completion-gate validation.
- **Artifact drift:** compare linked artifacts against a completion baseline and reject drift.
- **Boundary confusion:** keep Hermes, Ginflow core, plugin, skill, and target-project ownership distinct.

## Known gaps and architecture-vs-code inventory

| Finding | Classification | Evidence | User impact / next step |
|---|---|---|---|
| Hermes runtime and Kanban storage are not implemented here | Optional external boundary | `skills/ginflow/SKILL.md` core split | Runtime consumers must provide their own execution and Kanban integration |
| No committed package manifest pins Python or external tool versions | Confirmed gap | Repository file inventory; `Makefile` and scripts | Reproducibility depends on the host environment; document or add a manifest only as separately approved work |
| Target-project verification is not universal | Intentional boundary | `skills/ginflow/SKILL.md` target verification rules | Each target repo must declare its own canonical command |
| Optional CodeGraph/MCP checks are advisory | Confirmed behavior | `skills/ginflow/scripts/validate-harness.py` and optional-tool design plan | Missing optional tooling should warn, not block core work |
| Draw.io and Markdown architecture views are maintained separately | Confirmed maintenance risk | `docs/architecture/ginflow-flow.md` states Draw.io is canonical | Diagram changes require updating derived Markdown; automated synchronization is not present |
| Runtime identity and integration configuration are outside this repository's product scope | Intentional boundary | `AGENTS.md`, `skills/ginflow/SKILL.md` | Consumers configure their runtime separately; this repository remains standalone |
| Exact transitive dependencies, deployment topology, and production SLOs are unknown | Explicit unknown | No committed manifest/deployment contract found | Do not present them as guarantees; investigate only with a separately scoped task |

## Pros and cons for users

### Pros

- Clear separation between clarification, Direct Work, and Governed Work.
- Evidence-oriented Kanban completion rather than chat-only status.
- Reusable workflow guidance across target repositories.
- Explicit ownership boundaries reduce accidental runtime coupling.
- Standard-library-heavy repository implementation keeps the artifact layer small.
- Optional tooling can improve navigation without blocking core verification.

### Cons and trade-offs

- The workflow adds ceremony for work that is not clearly XS/S.
- Users must understand both Hermes-native Kanban states and Ginflow logical states.
- Documentation and diagrams are distributed across skill, plugin, core, and target-project boundaries.
- The artifact repository cannot guarantee target-project behavior; two verification commands may be necessary.
- Environment-specific Hermes, optional MCP, and target-toolchain dependencies reduce out-of-the-box reproducibility.
- The completion gate is intentionally strict: incomplete links, drift, or missing evidence stop completion rather than silently repairing claims.

## Reading order

1. [`../../README.md`](../../README.md) — project overview and commands.
2. [`ginflow-flow.md`](./ginflow-flow.md) — route and ownership flow.
3. [`gin-harness-system.drawio`](./gin-harness-system.drawio) — editable architecture source.
4. [`../../skills/ginflow/SKILL.md`](../../skills/ginflow/SKILL.md) — normative workflow contract.
5. [`../../plugins/ginflow-gate/`](../../plugins/ginflow-gate/) and [`../../core/ginflow-core/`](../../core/ginflow-core/) — implementation evidence.
6. [`../specs/GINFLOW-14.md`](../specs/GINFLOW-14.md) — this documentation task's contract.
