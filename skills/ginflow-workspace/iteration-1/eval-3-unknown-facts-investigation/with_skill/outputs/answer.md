# PAY-42 readiness

## Decision

**Not ready for direct build. Route to investigation first.**

Material inputs needed to locate, design, and verify change are unknown. Building now would require inventing provider behavior, event identity, retry semantics, storage design, repository location, or completion command.

## Smallest safe artifact set

Paths below are relative to real target repository, once Gin identifies it:

- `docs/briefs/PAY-42.md`
- `docs/plans/PAY-42.md`

No spec yet. Investigation must establish webhook contract and failure behavior first. Add `docs/specs/PAY-42.md` only after findings exist and exact behavior needs stable review before implementation. Do not create target-repo artifacts until repository path is confirmed.

## `docs/briefs/PAY-42.md`

```markdown
---
status: blocked
size: TBD
scope: payment webhook processing
owner: TBD — Gin must name payment-system owner
---

# Brief — PAY-42 payment webhook idempotency

## Objective

Ensure repeated delivery of one payment webhook event does not apply payment side effects more than once.

## Scope

- Investigate current payment webhook ingress and processing flow.
- Establish provider event identity and retry/acknowledgement contracts.
- Establish current persistence and transaction boundaries relevant to duplicate processing.
- Define observable implementation acceptance and canonical verification path from repository evidence.
- Implementation scope and affected paths: TBD — blocked on target repository and investigation findings; owner: payment-system owner.

## Acceptance criteria

- [ ] Real target repository and webhook entry point are identified from project evidence.
- [ ] Payment provider and authoritative event identifier contract are documented from provider/project evidence, including identifier scope and stability.
- [ ] Required HTTP response behavior for first delivery, duplicate delivery, processing failure, and provider retry is documented from authoritative evidence.
- [ ] Existing persistence technology, relevant schema/state, transaction boundary, and concurrency behavior are documented from repository/runtime evidence.
- [ ] Canonical project verification command is identified from target-repository documentation or automation and its baseline result is recorded.
- [ ] Proposed build acceptance includes: repeated delivery of the same authoritative event applies payment side effects once, including concurrent duplicate delivery if the confirmed system can receive it.
- [ ] Remaining unknowns are explicitly marked `TBD` with an owner or blocking decision.

## Non-goals

- Implement webhook idempotency before investigation resolves material contracts.
- Select or add persistence technology without target-repository evidence and an approved decision.
- Change payment-provider configuration, unrelated payment flows, or retry policy during investigation.

## Open questions / blockers

- Target repository absolute path: TBD — Gin must provide or identify it.
- Payment provider: TBD — payment-system owner must confirm from configuration/documentation.
- Authoritative event identifier and uniqueness scope: TBD — payment-system owner must confirm against provider contract.
- Retry and HTTP response semantics: TBD — payment-system owner must confirm against provider contract and current integration.
- Persistence technology and transaction guarantees: TBD — investigator must derive from target repository/runtime configuration.
- Canonical verification command: TBD — investigator must derive from target-repository rules or CI configuration.
```

## `docs/plans/PAY-42.md`

```markdown
# Plan — PAY-42 payment webhook idempotency investigation

1. Confirm target repository.
   - Owner: Gin.
   - Decision required: provide or select real absolute repository path for PAY-42.
   - Evidence: repository path plus applicable `AGENTS.md` / `.hermes.md` rules.
   - Stop if repository remains unknown; do not dispatch implementation.

2. Trace webhook integration in confirmed repository.
   - Locate provider configuration, webhook route/handler, downstream side effects, and existing tests.
   - Record provider and affected paths only from repository or authoritative integration evidence.
   - Evidence: file paths and concise processing-flow notes.
   - Covers brief criteria 1 and 2.

3. Resolve delivery contract with payment-system owner.
   - Confirm authoritative event ID field, uniqueness scope, stability, and behavior when ID is absent or malformed.
   - Confirm required HTTP status/body behavior for first delivery, duplicate delivery, validation failure, transient processing failure, and permanent failure; record which responses trigger provider retry.
   - Evidence: links or citations to provider documentation and approved owner decisions.
   - Covers brief criteria 2 and 3.

4. Inspect persistence and failure boundaries.
   - Identify existing persistence technology, relevant records/constraints, side-effect ordering, transaction boundaries, concurrency model, and recovery behavior.
   - Do not select a new table, lock, queue, cache, or dependency during investigation.
   - Evidence: repository paths plus observed guarantees and gaps.
   - Covers brief criterion 4.

5. Establish verification baseline.
   - Derive canonical verification command from target-repository documentation, scripts, or CI; do not guess it.
   - Run it in confirmed target repository and record exact command, exit result, and relevant output.
   - Evidence: fresh baseline result.
   - Covers brief criterion 5.

6. Produce build-ready contract.
   - Update brief with bounded implementation scope, exclusions, and observable acceptance based on findings.
   - Create `docs/specs/PAY-42.md` only if exact duplicate, retry, concurrency, partial-failure, or compatibility behavior needs a reviewed contract.
   - Add implementation plan steps only after affected paths and project-native verification are known.
   - Evidence: no material `TBD` remains; each remaining non-material `TBD` has owner; task answers what changes, where, how done is judged, and what must not change.
```

## Exact next action

Gin must identify the real target repository absolute path and payment-system owner. Then assign PAY-42 as an **investigation**, starting with repository-local rules and webhook entry-point tracing. Direct build remains blocked until investigation records all six unknown facts and canonical baseline verification evidence.
