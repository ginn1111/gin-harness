# PAY-42 readiness

## Decision

**Not ready for direct build. Route to investigation.**

Material inputs missing:
- payment provider
- absolute target repository path
- provider event identifier contract
- retry response semantics
- persistence technology and available uniqueness/transaction mechanisms
- canonical project verification command

Idempotency behavior, storage design, response behavior, implementation location, and completion evidence depend on these facts. Inventing any would create payment-processing risk.

## Smallest safe artifact set

Kanban card remains live state. Add only investigation brief and plan. Do not create spec or implementation yet; contract facts needed first.

Target-repo-relative paths, valid only after absolute target repository path is confirmed:

- `briefs/PAY-42.md`
- `plans/PAY-42.md`

No target-repo files should be written before workspace confirmation.

## `briefs/PAY-42.md`

```markdown
---
status: draft
size: M
scope: payment webhook idempotency investigation
owner:
---

# Brief — PAY-42 payment webhook idempotency

## Objective
Establish verified implementation facts and a build-ready contract for idempotent payment webhook processing.

## Scope
- Identify payment provider and webhook processing entry point in confirmed target repository.
- Confirm provider event identifier contract, including uniqueness and stability across retries.
- Confirm required HTTP response semantics for duplicate delivery, successful processing, transient failure, and permanent failure.
- Identify persistence technology and existing transaction/uniqueness facilities.
- Identify canonical project verification command.
- Produce build-ready acceptance criteria and implementation scope from verified evidence.

## Acceptance criteria
- [ ] Absolute target repository path is confirmed.
- [ ] Local `AGENTS.md` / `.hermes.md` rules are read when present.
- [ ] Payment provider and webhook entry point are recorded with repository evidence.
- [ ] Event identifier contract is recorded from authoritative provider documentation or existing verified project contract.
- [ ] Retry response semantics are recorded from authoritative provider documentation or existing verified project contract.
- [ ] Persistence technology and usable transaction/uniqueness mechanism are recorded from repository evidence.
- [ ] Canonical verification command is recorded and baseline result captured from target repository.
- [ ] Build scope, non-goals, and behavior-based acceptance criteria are updated without assumptions.

## Non-goals
- Implement webhook changes before required facts are verified.
- Select provider-specific identifiers, HTTP status codes, persistence schema, or verification commands by assumption.
- Change unrelated payment behavior.

## Notes
Current blockers: provider, repository path, event identifier contract, retry response semantics, persistence technology, and canonical verification command are unknown.
```

## `plans/PAY-42.md`

```markdown
# Plan — PAY-42 payment webhook idempotency investigation

1. Confirm absolute target repository path and set PAY-42 workspace to `dir:/abs/path/to/project` or an approved worktree.
2. Read target-repo `AGENTS.md`, `.hermes.md`, PAY-42 card, and linked artifacts.
3. Locate webhook entry point, payment provider integration, persistence layer, and existing webhook tests.
4. Verify event identifier and retry/response contracts against authoritative provider documentation or an existing verified project contract.
5. Record persistence transaction and uniqueness capabilities; do not choose a design before this evidence exists.
6. Identify and run canonical project verification command to capture baseline evidence.
7. Update PAY-42 brief; add `specs/PAY-42.md` only if verified behavior/contract detail would otherwise drift.
8. Return PAY-42 for build only when what to change, where to change it, how completion is judged, and what not to touch are explicit.
```

## Kanban card content

```text
Title: Investigate payment webhook idempotency

Objective:
- Establish verified provider, repository, event identity, retry response, persistence, and verification contracts needed to make PAY-42 build-ready.

Scope:
- Investigation only; no payment webhook implementation until material unknowns are resolved.

Acceptance:
- Required facts are evidenced, baseline verification is recorded, and linked brief contains explicit build scope, non-goals, and behavior-based acceptance criteria.

Workspace:
- BLOCKED: absolute target repository path not provided

Artifact links:
- briefs/PAY-42.md (create in confirmed target repo)
- plans/PAY-42.md (create in confirmed target repo)
```

## Next action

Gin supplies or confirms absolute target repository path and payment provider. Then investigator inspects local rules and code, verifies remaining contracts from repository/provider evidence, and records canonical baseline verification. Keep PAY-42 blocked from direct build until investigation acceptance criteria pass.
