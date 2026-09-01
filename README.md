
# Gin-harness

Gin-harness is the setup and integration repository that makes Hermes Agent work safer to route, execute, verify, and complete. It provides the shared **Ginflow** workflow, reusable core primitives, the `ginflow-gate` Hermes plugin, target-project starter context, architecture diagrams, and deterministic integration tests.

It is **not** a product application. Target repositories own product code, local rules, tests, and canonical product verification. Hermes Agent remains the runtime authority for profiles, skill loading, tools, Kanban, and lifecycle execution.

## Why Gin-harness exists

Gin-harness is a wrapper around Hermes Kanban. It gives Hermes Kanban a practical blueprint for effective work: documents that define scope and evidence, routing that shapes work before execution, state-transition guidance, gates that prevent unsupported completion, and document extensions for project-specific context.

For each work size, Ginflow guides the agent to use Hermes Kanban with the right level of structure:

- **Clarification:** unresolved requirements, cause, risk, ownership, workspace, or verification stay read-only until clear.
- **Direct Work (XS/S):** localized, reversible work can proceed without a card when every eligibility condition is affirmative.
- **Governed Work (M/L/XL or risky):** Hermes Kanban card, optional Spec/Plan, canonical verification, review, and evidence-backed completion apply.

Ginflow does not replace Hermes Kanban. Hermes remains authority for cards, assignments, lifecycle states, and review transitions. Ginflow provides routing and worker guidance; `ginflow-gate` validates required evidence at native transitions; linked documents, `.ginflow.yaml`, and artifact baselines extend Kanban with the context needed to make work restartable and auditable.

The system architecture in [`docs/architecture/gin-harness-system.drawio`](docs/architecture/gin-harness-system.drawio) shows this boundary: Hermes Kanban carries work state, while Ginflow supplies the routing, documents, guidance, verification, and gates around it.

## What is in the repository

| Area | Purpose | Primary evidence |
|---|---|---|
| `skills/ginflow/` | Normative workflow vocabulary, routing/output rules, startup, completion, artifact layout, and distributed harness validation | `skills/ginflow/SKILL.md`, `skills/ginflow/lib/harness_core.py` |
| `core/ginflow-core/` | Reusable routing primitives | `core/ginflow-core/routing.py` |
| `plugins/ginflow-gate/` | Hermes hooks, routing context, completion enforcement, feedback/recovery helpers | `plugins/ginflow-gate/plugin.yaml`, `plugins/ginflow-gate/*.py` |
| `templates/` | Starter local rules and task/artifact templates for target projects | `templates/` |
| `docs/architecture/` | Editable Draw.io diagrams and derived architecture explanations | `docs/architecture/` |
| `docs/specs/`, `docs/plans/`, `docs/briefs/` | Governed work artifacts | `docs/{specs,plans,briefs}/` |
| `scripts/` | Installation, setup, verification, and test helpers | `scripts/` |
| `tests/` and component test scripts | Harness and integration verification | `Makefile` |

For the evidence-based component map, dependency inventory, gaps, and trade-offs, read [`docs/architecture/gin-harness-reference.md`](docs/architecture/gin-harness-reference.md). The editable architecture source is [`docs/architecture/gin-harness-system.drawio`](docs/architecture/gin-harness-system.drawio); [`docs/architecture/ginflow-flow.md`](docs/architecture/ginflow-flow.md) is its derived, GitHub-readable flow explanation.

## Mental model: who owns what

```text
User intent
    │
    ▼
Hermes runtime ── loads ──> Ginflow skill
    │                         │
    │                         └─ workflow vocabulary and output contract
    ├─ owns profiles, tools, Kanban, lifecycle
    │
    └─ invokes ginflow-gate plugin
                              │
                              ├─ injects bounded routing guidance
                              └─ validates governed completion

Ginflow core ── reusable routing/validation model

Target project ── product code, local rules, tests, canonical verification
```

The plugin provides context and gates; it does not replace Hermes, inspect skills to classify requests, create cards, or authorize Direct Work by itself. Ginflow core provides reusable primitives; the skill provides the operational contract Hermes follows. The target project remains the authority for product behavior and its canonical verification command.

## How work flows

1. **Startup:** use the real target repository, read `AGENTS.md`/`.hermes.md`, inspect Git state, and read the selected card when governed work applies.
2. **Routing:** evaluate Work Mode separately from Work Size and Risk Impact.
3. **Clarification:** if requirements, target, cause, risk, ownership, artifact need, or verification are unknown, inspect read-only and ask for clarity; do not mutate project state.
4. **Direct Work:** proceed without a card only when every eligibility factor is affirmatively established: clear target, known cause where relevant, genuine XS/S scope, localized reversible change, no actual Risk Impact, no governance artifact need, known verification, project permission, and an unowned single-worker workspace.
5. **Governed Work:** use a complete Kanban card for M/L/XL, risky, coordinated, or artifact-requiring work. Add a Spec when behavior/contract can drift and a Plan when ordering, investigation, rollback, coordination, or layered verification matters.
6. **Verification:** run the target project's canonical command and report setup-repository checks separately.
7. **Review and completion:** workers submit governed work with native `kanban_request_review` after canonical verification and linked-artifact finalization. Hermes Kanban owns the `running -> review -> done` lifecycle and reviewer rework loop; reviewers either call native `kanban_complete` to finish valid work or `kanban_request_changes` with a minimal handoff (`reason`, `evidence`, `next_action`) to return it for rework. `ginflow-gate` validates Ginflow-specific evidence at the native transition points; it does not own lifecycle state machinery.

Detailed routing and branch boundaries are in [`docs/architecture/ginflow-flow.md`](docs/architecture/ginflow-flow.md) and the normative contract in [`skills/ginflow/SKILL.md`](skills/ginflow/SKILL.md).

## Project context and evidence

Each target project keeps optional Ginflow context in `.ginflow.yaml` at its repository root:

```yaml
version: 1
ginflow:
  board: <Kanban board slug>
  workspace: /absolute/path/to/project
  worker:
    profile: <worker Hermes profile>
    provider: <provider name>
    model: <model name>
  trace: false
```

`board` and `workspace` are required. Board resolution uses explicit runtime override, `HERMES_KANBAN_BOARD`, this file, then Hermes active board. Missing context sends work to `/ginflow`; malformed, incomplete, or workspace-mismatched context fails closed. Ordinary verification reads config but does not initialize or rewrite it. The optional `worker` block supplies governed-card dispatch defaults; explicit card values win.

Set `ginflow.trace: true` to enable optional `ginflow-trace` logging under `<workspace>/.ginflow/logs/` (errors under `.ginflow/errors/`). `GINFLOW_LOG=1` enables tracing for one process; any other set value disables it. Trace defaults off and never falls back to setup-repo paths.

Completion evidence stays split:

- **Project verification:** target repo's exact canonical command, such as `make verify` or `./verify.sh`, run from target root. This proves product behavior and blocks completion when unavailable or failing.
- **Ginflow harness:** external setup/deployed-skill check against target and selected card. It validates card fields, workspace, acceptance, completion evidence, linked paths, `artifact_baseline`, and linked-artifact drift. Report result separately; harness unavailability does not replace project verification.
- **Profile installation:** setup-repo `bash scripts/verify.sh`, when checking installed profile wiring.

For completed cards, baseline metadata records one Git commit plus exact linked artifact paths. `ginflow-gate` validates this metadata and drift during native `kanban_request_review` and `kanban_complete`; later edits, missing paths, unavailable commits, or path-list mismatch block affected lifecycle use. It does not silently repair drift or replace target verification.

## Dependencies and limits

The repository intentionally has a small setup-layer implementation. It uses Python standard-library modules, POSIX shell tools, Make, Git, and Draw.io XML documents. No committed `pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml`, or requirements file was found, so exact third-party/transitive versions are environment-specific and are not invented here.

Runtime and external boundaries include:

- Hermes Agent and its native Kanban/tools/profile runtime;
- the active Hermes profile configuration and installed plugin/skill wiring;
- optional CodeGraph/MCP tooling, which is advisory and must not block core work; and
- each target project's own language/toolchain and canonical verification.

Consequently, Gin-harness cannot guarantee Hermes internals, target-project behavior, deployment topology, production SLOs, or exact environment versions. Those are explicit boundaries or unknowns, not hidden guarantees.

## Strengths and trade-offs

**Strengths**

- Makes ambiguity, risk, ownership, and completion evidence explicit.
- Reuses one workflow across multiple target repositories.
- Separates Hermes runtime authority from Ginflow guidance and plugin enforcement.
- Keeps optional developer tooling advisory instead of making it a hidden blocker.
- Provides deterministic setup, lint, test, and artifact-drift checks.

**Trade-offs**

- Governed work has more ceremony than a quick prompt-and-edit flow.
- Users must understand the relationship between Hermes physical states and Ginflow logical routes.
- Documentation and implementation evidence span skill, core, plugin, templates, scripts, and target projects.
- Target verification is necessarily project-specific, so setup and product checks may both be required.
- Strict completion validation rejects missing links, drift, or weak evidence instead of repairing them silently.

## Install and verify

Read [`INSTALL.md`](INSTALL.md) before installing shared profile integrations. Do not copy secrets or modify profile identity without explicit approval.

For this setup repository:

```bash
make lint
make test
```

`make test` runs the canonical lint, setup, harness-core, artifact-guidance, Kanban-harness, and `ginflow-gate` checks. For a target project, run that repository's declared canonical command as a separate verification result; Ginflow does not substitute setup checks for product checks.

## Architecture and further reading

- [Reference architecture, dependencies, gaps, and trade-offs](docs/architecture/gin-harness-reference.md)
- [Editable Draw.io architecture](docs/architecture/gin-harness-system.drawio)
- [Derived Ginflow flow](docs/architecture/ginflow-flow.md)
- [Ginflow workflow contract](skills/ginflow/SKILL.md)
- [`ginflow-gate` plugin](plugins/ginflow-gate/)
- [Reusable Ginflow core](core/ginflow-core/)
- [Installation guide](INSTALL.md)
- [Local setup rules template](templates/AGENTS.md)

## Project rules

See [`AGENTS.md`](AGENTS.md) for setup-repository boundaries, verification order, generated-file handling, and completion rules. Governed documentation for this alignment task is tracked in [`docs/briefs/GINFLOW-14.md`](docs/briefs/GINFLOW-14.md), [`docs/specs/GINFLOW-14.md`](docs/specs/GINFLOW-14.md), and [`docs/plans/GINFLOW-14.md`](docs/plans/GINFLOW-14.md).

_Gin-harness documents the workflow around execution; it does not replace the runtime or the target project._
