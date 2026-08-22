# Ginflow Canonical Output Routing Design

**Status:** validated in conversation

## Problem

Hermes can load skills from different distributions and folder structures. Those skills also prescribe different output locations and artifact types. For one task, `brainstorming` may request a design under `docs/plans/`, `plan` may write to `.hermes/plans/`, `to-spec` may write under `docs/specs/`, and `wayfinder` may create `docs/wayfinding/` artifacts.

Following every skill literally can create overlapping sources of truth. The problem is the output contract, not skill lookup or folder normalization.

## Decision

Ginflow owns canonical output routing. A selected skill owns its process, quality guidance, and content requirements, but its default output folder is subordinate to target-project rules, the selected Kanban card, and Ginflow’s artifact matrix.

The precedence order is:

```text
1. Target-project local rules
2. Explicit Kanban/card output contract
3. Ginflow work-size/output matrix
4. Selected skill instructions
5. Skill default output location
```

Do not normalize, move, or rewrite skill folder structures. Do not make `ginflow-gate` inspect skill files. Hermes loads the selected skill with `skill_view`, follows its process, and adapts its output into the canonical Ginflow destination.

## Card authority

The Kanban card is the minimum build-ready authority. Brief artifacts are removed from this workflow.

A build-ready card records:

```text
Objective: <outcome>
Work-mode: <brainstorming|investigation|implementation|verification|recovery>
Work-size: <XS|S|M|L/XL|risky>
Size-rationale: <concise evidence>
Scope:
- Included: <bounded scope>
- Excluded: <adjacent work not included>
Acceptance:
- <observable result>
Links:
- <canonical artifact path or none>
```

`Scope` carries both inclusion and exclusion. A separate `Non-goals` field is not required.

## Canonical durable outputs

| Purpose | Canonical output |
|---|---|
| XS/S clear implementation | Kanban card only; `Links: - none` |
| Behavioral design or contract | `docs/specs/<CARD-ID>.md` |
| Ordered implementation and verification | `docs/plans/<CARD-ID>.md` |
| Multi-session decision map | `docs/wayfinding/<MAP-ID>.md` |
| Durable architecture decision | Project ADR convention, otherwise `docs/adrs/` |
| Optional resume snapshot | `docs/handoffs/<CARD-ID>.md` |
| Temporary session-only plan | `.hermes/plans/` |

`.hermes/plans/` is temporary execution scaffolding. It is not a durable target-project Spec or Plan unless target-project rules explicitly declare it authoritative.

## Work-mode and size routing

```text
Unclear requirements
→ brainstorming in conversation only
→ no file and no build-ready card

Clear XS/S work
→ Kanban card only
→ Links: - none

M work
→ Kanban card + Spec + Plan

L/XL or risky work
→ Kanban card + Spec + Plan
→ ADR only for a durable architectural decision

Investigation
→ clarify the target in conversation
→ Kanban card + investigation Spec/Plan when build-ready
```

A skill may recommend an artifact, but Ginflow selects the canonical type and path. If `brainstorming` says to write a design under `docs/plans/` while Ginflow classifies the output as a behavior contract, the design content goes into `docs/specs/<CARD-ID>.md`. No parallel design file is created.

## Injected routing contract

`ginflow-gate` injects a compact contract before the agent acts. It does not call `skill_view`, write files, or mutate Kanban.

Example for M work:

```text
Work-mode: implementation
Work-size: M
Size-rationale: Multiple components require ordered verification.
Output: Spec + Plan
Spec-path: docs/specs/<CARD-ID>.md
Plan-path: docs/plans/<CARD-ID>.md
Skill action: load the selected skill with skill_view before acting.
```

Example for S work:

```text
Work-mode: implementation
Work-size: S
Size-rationale: One bounded component with focused verification.
Output: Kanban card only
Links: - none
```

Example for unresolved work:

```text
Work-mode: brainstorming
Output: conversation only
Do not create files or a Kanban card until requirements are clear.
```

## Conflict and fallback behavior

- Missing work mode or work size: stop and clarify; create no file.
- Missing card ID for durable output: stop; durable artifacts need deterministic names.
- XS/S without a durable artifact: require `Links: - none`.
- `none` is a sentinel, not a path; the gate must not resolve or baseline it.
- Output path outside the target workspace: block.
- Duplicate artifact request: update the selected authority artifact instead of creating another file.
- Existing authority artifact with conflicting content or status: stop and report drift.
- Project-local output conventions override Ginflow defaults when explicitly declared.
- Skill-specific folder conventions apply only when no higher-precedence contract selects an output.

## Responsibility boundaries

- **Target-project rules:** highest authority for local path conventions.
- **Kanban card:** work assignment, outcome, scope, acceptance, mode, size, rationale, links, status, and progress.
- **Ginflow:** work-size matrix, artifact authority, and canonical output selection.
- **`ginflow-gate`:** deterministic route validation and injected output contract.
- **Selected skill:** process and quality guidance within the selected output boundary.
- **Hermes:** calls `skill_view` and performs allowed work.

## Verification design

Use the existing `ginflow-gate` pre-LLM routing-context seam as the highest integration seam.

Verify externally visible behavior:

- XS/S produces card-only guidance and `Links: - none`.
- M/L/XL/risky produces canonical Spec/Plan paths.
- Brainstorming produces conversation-only guidance.
- Explicit card output overrides a selected skill’s default output folder.
- Project-local path rules override Ginflow defaults.
- Missing or conflicting metadata fails closed.
- `none` is accepted without filesystem resolution or artifact-baseline validation.
- The plugin never writes files or calls `skill_view`.
- Diagram terminology matches the card, Ginflow, plugin, skill, and output boundaries.

Canonical repository verification remains:

```bash
make lint
make test
```

## Out of scope

- Normalizing or moving skill directories.
- Rewriting third-party or shared skills.
- Semantic skill classification or similarity search.
- Automatic artifact creation by the plugin.
- Observability/telemetry, full orchestrator runtime, and formal security/privacy systems.
