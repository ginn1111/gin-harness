# Gin-harness

Gin-harness is a standalone artifact repository for safer agent work. It provides the shared **Ginflow** workflow, reusable routing and validation primitives, an optional `ginflow-gate` adapter, target-project starter context, and deterministic integration checks.

It is not a product application. Target repositories own product code, local rules, tests, and canonical product verification. Runtime-specific integrations, including Hermes skill/plugin loading, remain optional consumers of these artifacts.

## Four-phase Initiative lifecycle

Ginflow organizes large autonomous work around one stable Initiative: Discovery frames problem and boundaries; Shaping approves one artifact-first Execution Package v2; Execution authorizes immutable AFK Batches and isolated Work Units; Decision reconstructs context from exact evidence for human disposition. Integration success opens Decision, not completion. `approved_for_mr` completes Ginflow lifecycle; provider publication and merge remain separate.

Pure core contracts are versioned independently as `initiative/v1`, `execution_batch/v1`, `review_cycle/v1`, `decision_projection/v1`, `notification/v1`, and `merge_request_intent/v1`. Legacy v2 packages/cards without explicit Initiative linkage remain compatible. Hermes owns identity/Kanban/lifecycle/persistence; target repos own product behavior/canonical verification; adapters own Git/check collection and future gateway/provider transport. Projections are bounded and redacted; raw logs, secrets, personal data, prompts, and transcripts are excluded.

TUI, direct Hermes DB access, gateway transport/subscription setup, and provider-specific MR publication remain deferred.

## Why Gin-harness exists
ை
Gin-harness is a wrapper around Hermes Kanban. It gives Hermes Kanban a practical blueprint for effective work: documents that define scope and evidence, routing that shapes work before execution, state-transition guidance, gates that prevent unsupported completion, and document extensions for project-specific context.

For new initiatives, the four-phase lifecycle above is canonical: Discovery resolves ambiguity, Shaping approves artifacts, Execution dispatches blocked cards, and Decision awaits human disposition. Hermes Kanban remains lifecycle authority.

**Legacy v1 compatibility only:** active cards created before artifact-first rollout may retain Clarification, Direct Work (XS/S), and Governed Work (M/L/XL or risky) routing until closure. This path does not apply to new initiatives and cannot bypass a selected `workflow_version: 2` package.

- **Clarification:** legacy-v1 unresolved requirements stay read-only until clear.
- **Direct Work:** legacy-v1 eligible localized reversible work may proceed without a card when every eligibility condition is affirmative.
- **Governed Work:** legacy-v1 larger or risky work uses a complete Kanban card and evidence-backed completion.

Do not use legacy labels to route new Initiative records.

Ginflow does not replace Hermes Kanban. Hermes remains authority for cards, assignments, lifecycle states, and review transitions. Ginflow provides routing and worker guidance; `ginflow-gate` validates required evidence at native transitions; linked documents, `.ginflow.yaml`, and artifact baselines extend Kanban with the context needed to make work restartable and auditable.

The system architecture in [`docs/architecture/gin-harness-system.drawio`](docs/architecture/gin-harness-system.drawio) shows this boundary: Hermes Kanban carries work state, while Ginflow supplies the routing, documents, guidance, verification, and gates around it.

The derived four-phase flow in [`docs/architecture/ginflow-flow.md`](docs/architecture/ginflow-flow.md) records Decision as the human boundary after Integration; Draw.io remains canonical for the repository-wide system diagram.

- **Clarification** keeps unresolved work read-only until the missing facts are known.
- **Direct Work** allows affirmatively eligible, localized XS/S changes without a card.
- **Governed Work** uses a complete Kanban card for larger, risky, coordinated, or artifact-requiring work.
- **Completion gates** validate card fields, verification evidence, linked artifacts, baseline commits, and drift.

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
4. For new governed/autonomous work, create or select one Initiative and follow Discovery → Shaping → Execution → Decision.
5. For active legacy-v1 cards only, retain their recorded Clarification/Direct Work/Governed Work route; do not apply it to new Initiatives.
6. Use the selected card's workspace, scope, acceptance, assignee, and linked artifacts.
7. Run the target project's canonical verification command.
8. Complete governed work with the native `kanban_complete` tool so `ginflow-gate` can validate the result.

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

1. **Startup:** use the real target repository, read `AGENTS.md`/`.hermes.md`, inspect Git state, and read the selected card when governed work applies.
2. **New Initiative routing:** use Discovery → Shaping → Execution → Decision; resolve ambiguity during Discovery/Shaping, not mid-execution.
3. **Legacy v1 routing:** active pre-migration cards may retain Work Mode, Work Size, Clarification, Direct Work, and Governed Work until closure. These labels are compatibility guidance only.
4. **Verification:** run the target project's canonical command and report setup-repository checks separately.
5. **Review and completion:** workers submit governed work with native `kanban_request_review` after canonical verification and linked-artifact finalization. Hermes Kanban owns the `running -> review -> done` lifecycle and reviewer rework loop; reviewers either call native `kanban_complete` to finish valid work or `kanban_request_changes` with a minimal handoff (`reason`, `evidence`, `next_action`) to return it for rework. `ginflow-gate` validates Ginflow-specific evidence at the native transition points; it does not own lifecycle state machinery.

New Initiative records must not use legacy routing as an execution bypass.

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
- **Profile installation:** setup-repo `make verify`, when checking installed profile wiring.

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
- [Target-project setup template](templates/AGENTS.md)

## Project rules

See [`AGENTS.md`](AGENTS.md) for repository boundaries, verification order, generated-file handling, and completion rules.

_Gin-harness documents the workflow around execution; it does not replace Hermes Agent or the target project._
