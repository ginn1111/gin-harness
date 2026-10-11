---
status: completed
size: XL
scope: Ginflow v2 artifact-first workflow
owner: gin
---

# Ginflow v2 — Artifact-First Execution Packages

## Problem Statement

Ginflow currently asks the agent to classify work by size and choose between Direct Work, Clarification, and Governed Work. This creates subjective routing, repeated pauses, and avoidable worker interruptions. Workers may begin with incomplete artifacts, discover missing decisions during execution, and stop mid-task for questions that should have been settled before dispatch.

The desired workflow front-loads brainstorming, feedback, specification, work splitting, planning, approval, and validation. Kanban workers should receive complete, committed execution packages and continue until done or until a narrowly defined exception makes safe progress impossible.


## Solution

Introduce Ginflow workflow version 2 around an artifact-first Execution Package.

Interactive Shaping happens before Kanban execution. During Shaping, the user and agent brainstorm, gather feedback, inspect the repository read-only, write a Work Contract and Spec, split the initiative into independently verifiable Work Units, and write one Plan per Work Unit. One final user approval covers the complete package.

After splitting, Ginflow creates blocked Kanban cards so each Work Unit has a durable execution record and stable links. The complete artifact package is committed and validated before any root card is unblocked. Dependency-gated cards wait for completed parents. Every implementation card runs in goal mode until it is done or reaches a defined Worker Exception. A final Integration Card verifies cross-unit behavior and global acceptance before the initiative completes.

Ginflow v2 removes Work Size, Direct Work, size-based routing, and conditional artifact selection. Clarification becomes part of Shaping rather than an execution route.

## User Stories

1. As Gin, I want to brainstorm before Kanban cards are dispatched, so that requirements can change cheaply before execution.
2. As Gin, I want to give feedback while the Work Contract and Spec are drafted, so that the execution package reflects my intent.
3. As Gin, I want one approval point for the complete execution package, so that I am not interrupted after every artifact.
4. As Gin, I want all required artifacts to exist before implementation starts, so that workers do not stop for routine clarification.
5. As Gin, I want Work Size removed, so that execution does not depend on subjective XS/S/M/L/XL classification.
6. As Gin, I want Direct Work removed, so that every new implementation has durable scope, acceptance, evidence, and ownership.
7. As Gin, I want unclear requirements handled during Shaping, so that ambiguity does not become a mid-execution blocker.
8. As Gin, I want the Work Contract to define initiative objective, boundaries, exclusions, global acceptance, and verification strategy, so that every Work Unit follows one authoritative contract.
9. As Gin, I want the Spec to define detailed behavior, interfaces, rules, edge cases, and constraints, so that workers do not invent product behavior.
10. As Gin, I want each Work Unit to have its own Plan, so that execution order and local verification remain explicit.
11. As Gin, I want work split by ownership, dependencies, bounded scope, and independent verification rather than estimated size, so that each unit is executable and reviewable.
12. As Gin, I want stable initiative and unit keys assigned during Shaping, so that artifacts can be named and linked before Hermes creates internal task IDs.
13. As Gin, I want execution cards created in blocked state, so that dispatch cannot race ahead of incomplete artifacts.
14. As Gin, I want package validation before cards are unblocked, so that no worker starts from an incomplete or inconsistent package.
15. As Gin, I want root cards unblocked together after approval and validation, so that independent work can begin without more manual approvals.
16. As Gin, I want child cards gated by parent completion, so that dependent work cannot run against unverified prerequisites.
17. As Gin, I want parallel Work Units to use isolated workspaces or worktrees, so that workers cannot collide in one mutable checkout.
18. As Gin, I want shared mutable workspaces to force sequential execution, so that concurrent changes remain safe.
19. As a Kanban worker, I want a complete Work Contract, Spec, Plan, scope, acceptance criteria, dependencies, and verification commands before dispatch, so that I can work continuously.
20. As a Kanban worker, I want authority to choose implementation details within approved boundaries, so that ordinary engineering decisions do not require user intervention.
21. As a Kanban worker, I want authority to inspect code, modify card-scoped files, add tests, rerun checks, and fix failures caused by my changes, so that I can finish the unit autonomously.
22. As a Kanban worker, I want to revise Plan implementation steps without stopping when contract, scope, acceptance, dependencies, and verification remain unchanged, so that the Plan can reflect discoveries.
23. As a Kanban worker, I want goal-mode execution, so that I continue across turns until completion or a defined exception.
24. As a Kanban worker, I want a default turn budget of 20, an expected-complexity budget of 40, and a hard maximum of 60, so that long work is bounded without Work Size labels.
25. As a Kanban worker, I want normal compile failures and test failures caused by my changes treated as work rather than exceptions, so that I do not stop prematurely.
26. As a Kanban worker, I want a precise Worker Exception definition, so that I know when stopping is justified.
27. As a Kanban worker, I want repeated attempts to continue while they produce new evidence or reduce failure scope, so that recoverable failures do not interrupt Gin.
28. As a Kanban worker, I want to stop after the same root cause survives three materially different fixes, so that goal mode does not loop uselessly.
29. As a Kanban worker, I want to stop after two investigation turns produce no new evidence, so that stalled investigation becomes explicit.
30. As a Kanban worker, I want unavailable external dependencies, exhausted runtime budgets, unsafe scope expansion, policy conflicts, workspace collisions, and newly discovered material risks classified as exceptions, so that unsafe progress stops.
31. As Gin, I want only `needs_input` exceptions to interrupt me, so that dependency, capability, and transient conditions use their proper lifecycle handling.
32. As a maintainer, I want exception handoffs to record completed work, exact blocker, evidence, attempted fixes, changed files, verification result, smallest required decision, and resume step, so that work resumes cleanly.
33. As a maintainer, I want a blocked worker to report one complete handoff rather than repeated clarification messages, so that the task thread stays useful.
34. As a reviewer, I want workers to submit only after local acceptance and verification pass, so that review starts from a credible completion claim.
35. As a reviewer, I want to complete valid work or return exact evidence and a next action without editing implementation, so that ownership remains clear.
36. As a returned worker, I want to resume the same goal loop after review changes, so that rework does not need a new card or user approval.
37. As Gin, I want independent branches to continue when another branch is blocked, so that one exception does not halt unrelated work.
38. As Gin, I want descendants of a failed unit to remain gated, so that invalid prerequisites cannot propagate.
39. As Gin, I want a mandatory Integration Card after implementation units, so that cross-unit failures have explicit ownership.
40. As an integration worker, I want authority to fix cross-unit problems within the approved Contract and Spec, so that compatible unit-level changes can be completed without reshaping.
41. As Gin, I want initiative completion to require every required card, global acceptance, integration verification, clean artifact baselines, and zero unresolved exceptions, so that completion is evidence-backed.
42. As Gin, I want partial completion allowed only after the package is revised and reapproved, so that cancelled work never silently weakens global acceptance.
43. As Gin, I want whole-initiative cancellation to archive unfinished cards and cancel the Work Contract, so that lifecycle state remains truthful.
44. As Gin, I want unit cancellation to trigger impact analysis and package reapproval, so that dependencies and acceptance remain coherent.
45. As Gin, I want material changes discovered during execution to pause affected cards and return impacted artifacts to Shaping, so that workers do not silently expand approved work.
46. As Gin, I want unaffected independent cards to continue while an impacted branch is reshaped, so that reapproval remains scoped.
47. As a maintainer, I want new initiatives piloted under explicit version 2 before default cutover, so that real workflow friction is found safely.
48. As a maintainer, I want Contract states for draft, approved, active, completed, and cancelled, so that initiative lifecycle is explicit.
49. As a maintainer, I want Spec and Plan states for draft, approved, active, completed, superseded, and cancelled, so that supporting artifact lifecycle is explicit.
50. As Gin, I want approval identity and UTC time recorded on the Work Contract, so that approval is auditable.
51. As a maintainer, I want all execution cards bound to the same committed package baseline, so that workers use one approved artifact snapshot.
52. As a maintainer, I want artifact drift checks preserved through review and completion, so that linked documents cannot change silently.
53. As a maintainer, I want canonical project verification preserved, so that Ginflow evidence never substitutes for product behavior checks.
54. As a maintainer, I want one deterministic package validator, so that approval readiness has a single observable result.
55. As a maintainer, I want validation to reject missing or unapproved artifacts, duplicate keys, broken links, cyclic dependencies, incomplete fields, unsafe workspace overlap, dirty linked paths, and missing baseline evidence, so that invalid packages fail before dispatch.
56. As a documentation owner, I want to create new Work Contract and artifact-first workflow documentation, so that version 2 is understandable.
57. As a documentation owner, I want every Ginflow workflow document audited, so that stale size-based behavior is not missed.
58. As a documentation owner, I want README, skill guidance, architecture material, starter guidance, examples, and diagrams updated together, so that users see one consistent workflow.
59. As a documentation owner, I want references and links checked during lifecycle verification, so that documentation CRUD does not leave broken navigation.
60. As a future maintainer, I want canonical definitions for Shaping, Work Contract, Execution Package, Work Unit, Package Approval, Worker Exception, and Integration Card, so that code and documentation share one language.
61. As a future maintainer, I want an architectural decision record for artifact-first execution, so that the removal of Direct Work and Work Size remains understandable.

## Implementation Decisions

- Introduce `workflow_version: 2` as the explicit selector for artifact-first initiatives. A linked version 2 Work Contract selects the new flow.
- Replace pre-execution route selection with **Shaping**. Shaping includes brainstorming, feedback, read-only repository investigation, artifact drafting, work splitting, dependency design, and package approval.
- Permit artifact creation before Kanban cards exist. Prohibit product-code mutation, implementation dispatch, and execution commands during Shaping.
- Define **Work Contract** as the initiative authority for objective, boundaries, exclusions, global acceptance, and verification strategy.
- Define **Spec** as the detailed behavior authority for interfaces, rules, edge cases, and constraints.
- Define **Work Unit** as one independently executable unit with one owner, bounded scope, observable acceptance, explicit dependencies, a known workspace, and canonical verification.
- Define **Plan** as the ordered implementation and local verification description for one Work Unit.
- Define **Execution Package** as one approved Work Contract, one approved Spec, the complete Work Unit split, one approved Plan per Work Unit, dependency graph, workspace allocation, verification strategy, and final Integration Card.
- Require one stable user-provided `WORK-KEY` for the initiative and one shaping-time `UNIT-KEY` per Work Unit. Hermes internal task IDs remain runtime identifiers and do not determine artifact names.
- Use one canonical **provider document** per Work Unit, hosted by exactly one provider: `local` (consolidated Markdown record), `github` (GitHub Issue), or `linear` (Linear Issue). Contract, Spec, and Plan are semantic sections of the normalized **Work Package**, not separate stored artifacts. Supersedes the earlier repository-local-only decision; see ADR 0001 and "Provider documents" below.
- Require one explicit user approval for the complete package. The Work Contract records approver identity and RFC3339 UTC approval time. Spec and Plans inherit approval through the committed package baseline.
- Create Kanban cards after work splitting, with complete future links and blocked initial state. Create all cards before execution begins.
- Bind every card to the same committed package baseline. Store the baseline in Kanban/package-validation evidence rather than self-referencing it from inside the commit.
- Validate the complete package once before execution. Unblock root cards only after package approval, clean artifact commit, baseline verification, and successful package validation.
- Keep child cards parent-gated until every parent is `done`. `review` does not satisfy a dependency.
- Require one card and Plan per Work Unit. Require a final Integration Card after all required implementation branches.
- Use dependency and verification boundaries instead of Work Size. Remove XS/S/M/L/XL vocabulary, Direct Work, size-based routing, and conditional Spec/Plan selection from version 2.
- Keep Clarification as an activity inside Shaping. It is no longer an execution route.
- Dispatch implementation cards with goal mode enabled. Use 20 turns by default, 40 for known investigation-heavy or migration work, and 60 as the hard maximum. Budget selection is not Work Size.
- Allow workers to choose implementation details, inspect code, modify card-scoped files, add or adjust tests, rerun verification, fix failures caused by their changes, update progress, and revise non-contractual Plan steps.
- Prohibit workers from changing objective, scope, acceptance, specified public behavior, dependencies, security boundaries, or verification contracts without returning affected work to Shaping.
- Define a Worker Exception as one of: blocking contract contradiction or missing requirement; unavailable dependency, credential, permission, service, or tool; policy or security conflict; repeated out-of-scope canonical verification failure; required scope expansion; newly discovered data-loss, migration, compatibility, deployment, concurrency, privacy, or security risk; workspace collision; or exhausted runtime budget.
- Do not treat ordinary compile failures, worker-caused test failures, unfamiliar code, or implementation choices as exceptions.
- Continue retries while attempts produce new evidence or reduce failure scope. Stop when the same root cause survives three materially different fixes, two investigation turns yield no new evidence, an external dependency remains unavailable, or the goal budget expires.
- Route exceptions by cause: human/contract decisions to `needs_input`, task dependencies to `dependency`, missing access or impossible operations to `capability`, and flaky infrastructure to `transient`.
- Require one structured exception handoff containing completed work, exact blocker, evidence, attempted fixes, changed files, verification result, smallest required decision, and exact resume step.
- Let independent branches continue when one branch blocks. Keep failed-card descendants and the Integration Card dependency-gated.
- Require reviewers to approve or return changes; reviewers do not repair implementation. Returned workers resume the same goal loop without user interruption unless a Worker Exception exists.
- Permit Plan implementation-step changes during execution without reapproval when objective, scope, acceptance, dependencies, behavior, and verification remain unchanged.
- Return material Contract, Spec, split, dependency, scope, acceptance, or verification changes to draft Shaping. Pause affected cards, revise impacted artifacts, obtain package reapproval, commit a new baseline, revalidate, and resume. Independent unaffected cards may continue.
- Complete an initiative only after every required card is done, global acceptance passes, Integration Card verification passes, linked artifacts match completion baselines, and no unresolved Worker Exception remains.
- Cancel a whole initiative by archiving unfinished cards and marking the Contract cancelled. Cancel a unit only after impact analysis; reshape and reapprove whenever global acceptance or dependencies change.
- Add a deterministic package validator covering artifact states, required sections, unique keys, exact links, dependency cycles, owners, workspaces, simultaneous workspace safety, clean committed artifact paths, and baseline project verification.
- Preserve Hermes Kanban as lifecycle authority, project-native canonical verification, review transitions, evidence-backed completion, artifact drift checks, workspace isolation, and setup-repository versus target-repository boundaries.
- Create a domain glossary containing Shaping, Work Contract, Execution Package, Work Unit, Package Approval, Worker Exception, and Integration Card.
- Record the artifact-first workflow choice in an ADR because it is hard to reverse, surprising without context, and chosen over a materially different size-based alternative.

## Testing Decisions

- Prefer external behavior over implementation details. Tests should assert observable routing, artifact state, Kanban lifecycle, validation outcomes, dispatch behavior, worker exception handling, review transitions, and completion evidence.
- Use one primary high-level seam: the existing end-to-end Ginflow lifecycle integration test. It should exercise Shaping output, blocked card creation, package validation, root unblocking, dependency gating, goal-mode execution, exception behavior, review, Integration Card ordering, drift validation, and initiative completion.
- Extend the lifecycle seam to prove that no product-code execution begins before the complete approved package is committed and validated.
- Extend the lifecycle seam to prove that valid independent root units can run concurrently only in isolated workspaces, while shared mutable workspace units remain sequential.
- Extend the lifecycle seam to prove that child units remain gated until all parents are `done`.
- Extend the lifecycle seam to prove that the Integration Card runs after all required implementation units and owns global verification.
- Extend the lifecycle seam to prove that a material artifact revision returns affected work to Shaping and requires a new approved baseline before resume.
- Extend the lifecycle seam to prove that a blocked independent branch does not stop unrelated branches and that its descendants remain gated.
- Extend the lifecycle seam to prove cancellation and partial-completion rules.
- Add narrow plugin or validator unit tests only for failure cases that are difficult to observe precisely through the lifecycle test. Keep seams minimal.
- Unit-test package rejection for missing artifacts, non-approved states, missing required sections, duplicate keys, broken or mismatched links, cyclic dependencies, missing owners, unsafe concurrent workspace overlap, dirty linked paths, missing commits, and absent baseline verification.
- Unit-test Worker Exception classification and confirm ordinary implementation/test failures are not exceptions.
- Unit-test retry exhaustion thresholds and goal-turn budget enforcement.
- Unit-test card schema validation for Contract, Spec, Plan, dependencies, verification, workspace, assignee, goal mode, and turn budget.
- Preserve prior completion-gate and native review-transition tests as regression coverage for evidence, linked-artifact state, completion baselines, drift, request-changes, and final completion.
- Use existing plugin tests as prior art for deterministic guidance and gate failures.
- Use existing shell integration tests as prior art for command-level startup and setup behavior.
- Run canonical repository verification before declaring implementation complete: lint plus full deterministic test suite.

## Out of Scope

- Provider types other than `local`, `github`, and `linear`; GitHub Discussions, pull requests, repository files, or Linear documents as provider formats.
- Silent fallback to another provider, fuzzy adoption, or overwriting existing records.
- Provider credentials in core modules, project configuration, or the completion gate.
- Synchronizing provider fields other than mapped tracker Issue workflow status (assignment, labels, milestones, cycles, dependencies).
- Deriving package approval from chat history without an approved repository artifact and committed baseline.
- Automatic product implementation during Shaping.
- Allowing workers to expand objective, scope, acceptance, dependencies, specified behavior, security boundaries, or verification contracts without reapproval.
- Replacing Hermes Kanban, its native task states, dispatcher, reviewer lifecycle, or notification model.
- Replacing target-project canonical verification with Ginflow validation.
- Estimating effort through renamed size labels. Turn budgets are runtime bounds, not effort categories.
- Reviewer-authored implementation fixes.
- Completing an initiative based on percentage done or a subset of the original acceptance criteria.
- Reworking unrelated Ginflow tracing or setup behavior unless required by artifact-first lifecycle integration.

## Further Notes

- Canonical flow: `Shaping → Work Contract → Spec → Work Units and Plans → blocked cards → package approval and commit → package validation → root unblocking → goal-mode execution → review → Integration Card → initiative completion`.
- Artifact creation is part of Shaping and occurs before Kanban execution. Product-code mutation starts only after cards exist and the package passes its gate.
- “Run until done or exception” is the central worker design constraint. New prompts or pauses should not be added for decisions already delegated by the approved package.

## Provider documents

Architecture alignment for GitHub #18/#19. Runtime implementation (setup resolution, adapters) is out of scope here.

- **Provider document** — the single canonical governance record for one Work Unit, hosted by `local` (consolidated Markdown, frontmatter metadata), `github` (Issue), or `linear` (Issue; hidden machine metadata marker for remote providers). **Work Package** is the normalized, provider-neutral content (Contract, Spec, Plan, acceptance, verification, dependencies, risks) rendered into it.
- **Document reference** — provider-neutral `{provider, stable ID, path or URL}` replacing local-file-specific package links. Human-readable link lives in the card; structured reference in package/task metadata.
- **`document_baseline`** — one model for every provider; always includes normalized content hash. Hash covers rendered title plus body after newline, trailing-space, and final-newline normalization only; comments, labels, assignees, milestones, cycles, and provider status are excluded.
  - Local evidence: committed content plus Git commit.
  - Remote evidence: provider, stable ID, canonical URL, content hash, and fetch time. Adapter re-fetches before review and completion; evidence older than 5 minutes fails. `ginflow-gate` validates supplied evidence and freshness and holds no provider credentials.
  - Inaccessible, deleted, provider-mismatched, stale, or drifted records block transition (fail closed).
- **Provider resolution** — setup stores a strict project-local documentation block (`adaptive`, `local`, `github`, `linear`). Adaptive resolves from exact directives: project-portable agent instructions, then Hermes-specific, then linked agent docs, then existing canonical references; conflicts stop for user choice. Tool availability never selects policy. Targets use stable identities (GitHub repository; Linear team and optional project).
- **Creation and adoption** — a pure provider-document builder renders and hashes; adapters perform side effects. Remote writes need explicit approval. External records are created before Hermes cards; provider failure creates no card. Local flow keeps blocked-card-first safety. Exactly one metadata match may be adopted with confirmation; multiple matches block; title-only matches only warn. No silent fallback to another provider; no overwrite of conflicting content.
- **Authority** — Hermes Kanban stays lifecycle authority (status, assignment, workspace, dependencies, review, completion). Cards stay concise (Objective, Scope, Acceptance, Verification, dispatch dependencies, document link). Provider records carry no Hermes task backlink in v1; stable Work Unit key enables cross-search. Content freezes when the card starts running; later change needs explicit re-baseline and approval. Project-native verification remains behavior authority.
- **Tracker status sync (github/linear only)** — applies only to Issue workflow status via explicit setup-resolved mappings; local provider has none; provider document content/frontmatter is not rewritten. Workers sync start, block, resume, review-request; reviewers sync request-changes and successful completion. Provider update happens before the Hermes transition completes, then the adapter re-fetches fresh evidence. Missing/invalid mapping, update failure, or re-fetch mismatch fails closed with no partial-success claim. Assignment, labels, milestones, cycles, dependencies are never synced.
- **Newest schema only** — installed contract is authoritative; users do not select workflow versions. Outdated or malformed config permits read-only inspection but blocks governed creation.
