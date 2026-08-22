# Ginflow

Ginflow defines how work is clarified, routed, governed, executed, verified, and completed across setup and target-project repositories.

## Language

**Direct Work**:
Eligible XS/S implementation performed without a Kanban Card or Governance Artifact, with canonical verification and a scoped result report. `direct-no-card` may be used as a machine-facing route identifier.
_Avoid_: Fast path, no-card work, cardless work

**Governed Work**:
Work controlled by a build-ready Kanban Card and its lifecycle gates, with Spec or Plan artifacts when required.
_Avoid_: Card path, card flow

**Direct Work Eligibility**:
The complete set of facts that must be affirmatively established before Direct Work begins. An unknown factor does not count as safe or eligible.
_Avoid_: No known risk, assumed eligibility

**Clarification**:
A conversation-led state used when work requirements or routing facts are unresolved. It permits read-only investigation to establish facts, but creates neither a Kanban Card nor a Governance Artifact and permits no repository mutation.
_Avoid_: Unshaped work, preliminary card, working-note phase

**Read-only Investigation**:
Fact-finding that inspects the project or runs non-mutating diagnostics without changing governed project state. Its result returns to routing rather than becoming implementation.
_Avoid_: Direct Work, implementation

**Work Size**:
A shaping classification based on clarity, affected components and owners, behavior or contract impact, ordering, operational concerns, verification layers, and split needs. Raw file count, title wording, and semantic similarity are not size evidence by themselves.
_Avoid_: File-count estimate, title-based estimate

**Work Mode**:
The kind of activity Hermes determines from the request and project context, such as implementation, verification, recovery, or Clarification. It is evaluated separately from Work Size and Risk Impact.
_Avoid_: Route, size

**Routing Matrix**:
The Ginflow-core-owned structured decision model Hermes must use to evaluate Work Mode, Work Size, Risk Impact, Direct Work Eligibility, and the resulting route. The gate renders this authority for Hermes; semantic reasoning supplies facts to the matrix rather than replacing it with unconstrained judgment.
_Avoid_: Intuition-only routing, plugin classifier

**Risk Impact**:
A credible effect on security, privacy, data, migration, concurrency, deployment, compatibility, or rollback. Mentioning a risky subject without changing its behavior or controls is not Risk Impact.
_Avoid_: Risk keyword, risky topic

**Governance Artifact**:
A persistent document that governs behavior, execution order, architectural decisions, navigation, or resume state, such as a Spec, Plan, ADR, Wayfinder, or Handoff.
_Avoid_: Durable Artifact, output document

**Delivery Change**:
A modification to the product, project documentation, tests, configuration, or supporting implementation that delivers the requested result. It is not a Governance Artifact merely because it persists in the repository.
_Avoid_: Artifact

## Routing and output contract

Ginflow has exactly three routing outcomes:

- **Direct Work**: affirmatively eligible XS/S work. Declare `Route: direct-no-card`, Work Mode, Work Size, size rationale, output contract, and canonical verification in conversation. Produce the Delivery Change and conversation result only; create no Kanban Card, `Links` field, Brief, Governance Artifact, or replacement execution record.
- **Governed Work**: known M/L/XL size, actual Risk Impact, Governance Artifact need, or another known disqualifier. Use a build-ready Kanban Card. Add `docs/specs/<CARD-ID>.md` when behavior or contract can drift and `docs/plans/<CARD-ID>.md` when ordering, investigation, risk, rollback, coordination, or layered verification matters.
- **Clarification**: unresolved requirements, cause, Work Size, Risk Impact, workspace ownership, Governance Artifact need, or canonical verification. Permit conversation-led brainstorming and read-only investigation only; do not mutate the repository or create a card, working note, or Governance Artifact until facts are established.

Direct Work Eligibility is fail-closed and requires affirmative evidence for clear requirements and target behavior, known bug root cause, genuine XS/S size, localized reversible scope, no actual Risk Impact, no Governance Artifact need, known canonical verification, project-local permission, and an unowned single-worker workspace. Risky keywords and raw file count are not evidence by themselves. If scope, clarity, ownership, verification, or impact changes after Direct Work begins, stop mutation and reclassify before continuing.

Work Size is evaluated from clarity, cause/target knowledge, affected components and owners, contract impact, ordering, operational concerns, verification layers, and split needs—not title wording, word count, file count, or semantic similarity. Governed Work cards record `Work-mode`, `Work-size`, and `Size-rationale`.

Canonical output precedence is: target-project local rules, explicit route/card contract, Ginflow matrix, selected skill instructions, then skill defaults. Adapt selected-skill output instructions into the chosen Spec, Plan, Wayfinder, or Handoff rather than creating duplicates. `.hermes/plans/` is temporary session-plan storage unless target-project rules explicitly promote it.

The plugin injects deterministic candidate skill guidance; Hermes must call `skill_view(name='...')` before acting. The plugin does not inspect skills, perform semantic classification, create cards or Governance Artifacts, mutate Kanban, or mechanically authorize Direct Work.

## Feedback boundary

Feedback v1 is a pure, normalized lifecycle event contract for Governed Work only. It is not telemetry, analytics, persistence, notification, orchestration, or a classifier. Events require a stable `event_id` and Kanban `task_id`; Direct Work emits no normalized feedback event in v1. Existing lifecycle owners remain responsible for persistence and mutation.

Supported signals and next actions:

| Signal | Next action |
|---|---|
| `verification_passed` | `none` |
| `verification_failed` | `investigate` |
| `gate_rejected` | `repair_artifacts` |
| `artifact_drift` | `stop_and_inspect` |
| `blocked` | `investigate` |
| `recovered` | `resume` |
| `retry_exhausted` | `notify_human` |
| `human_corrected` | `resume` |
| `completed` | `none` |
