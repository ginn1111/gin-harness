Status: ready-for-agent

# Ginflow v2 — Artifact-First Execution Packages

## Problem Statement

Ginflow currently asks the agent to classify work by size and choose between Direct Work, Clarification, and Governed Work. This creates subjective routing, repeated pauses, and avoidable worker interruptions. Workers may begin with incomplete artifacts, discover missing decisions during execution, and stop mid-task for questions that should have been settled before dispatch.

The desired workflow front-loads brainstorming, feedback, specification, work splitting, planning, approval, and validation. Kanban workers should receive complete, committed execution packages and continue until done or until a narrowly defined exception makes safe progress impossible.

Related documentation also describes the current size-based workflow across several surfaces. It must be created, updated, or deleted as part of the migration so documentation, enforcement, tests, examples, and diagrams remain consistent.

## Solution

Introduce Ginflow workflow version 2 around an artifact-first Execution Package.

Interactive Shaping happens before Kanban execution. During Shaping, the user and agent brainstorm, gather feedback, inspect the repository read-only, write a Work Contract and Spec, split the initiative into independently verifiable Work Units, and write one Plan per Work Unit. One final user approval covers the complete package.

After splitting, Ginflow creates blocked Kanban cards so each Work Unit has a durable execution record and stable links. The complete artifact package is committed and validated before any root card is unblocked. Dependency-gated cards wait for completed parents. Every implementation card runs in goal mode until it is done or reaches a defined Worker Exception. A final Integration Card verifies cross-unit behavior and global acceptance before the initiative completes.

Ginflow v2 removes Work Size, Direct Work, size-based routing, and conditional artifact selection. Clarification becomes part of Shaping rather than an execution route. Existing active version 1 cards finish under legacy rules during migration.

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
47. As a maintainer, I want version 2 selected by a versioned Work Contract, so that legacy and artifact-first workflows can coexist during rollout.
48. As a maintainer, I want active legacy cards to finish under version 1 rules, so that migration does not invalidate work already underway.
49. As a maintainer, I want new initiatives piloted under explicit version 2 before default cutover, so that real workflow friction is found safely.
50. As a maintainer, I want version 1 removed after active legacy work closes, so that compatibility logic does not become permanent.
51. As a maintainer, I want Contract states for draft, approved, active, completed, and cancelled, so that initiative lifecycle is explicit.
52. As a maintainer, I want Spec and Plan states for draft, approved, active, completed, superseded, and cancelled, so that supporting artifact lifecycle is explicit.
53. As Gin, I want approval identity and UTC time recorded on the Work Contract, so that approval is auditable.
54. As a maintainer, I want all execution cards bound to the same committed package baseline, so that workers use one approved artifact snapshot.
55. As a maintainer, I want artifact drift checks preserved through review and completion, so that linked documents cannot change silently.
56. As a maintainer, I want canonical project verification preserved, so that Ginflow evidence never substitutes for product behavior checks.
57. As a maintainer, I want one deterministic package validator, so that approval readiness has a single observable result.
58. As a maintainer, I want validation to reject missing or unapproved artifacts, duplicate keys, broken links, cyclic dependencies, incomplete fields, unsafe workspace overlap, dirty linked paths, and missing baseline evidence, so that invalid packages fail before dispatch.
59. As a documentation owner, I want a dedicated documentation migration Work Unit, so that related documentation receives explicit ownership and acceptance criteria.
60. As a documentation owner, I want to create new Work Contract and artifact-first workflow documentation, so that version 2 is understandable.
61. As a documentation owner, I want every Ginflow workflow document audited, so that stale size-based behavior is not missed.
62. As a documentation owner, I want README, skill guidance, architecture material, starter guidance, examples, and diagrams updated together, so that users see one consistent workflow.
63. As a documentation owner, I want obsolete Work Size and Direct Work guidance deleted, so that removed concepts are not presented as valid version 2 behavior.
64. As a documentation owner, I want legacy version 1 guidance retained only where active-card compatibility requires it, so that migration rules remain precise.
65. As a documentation owner, I want references and links checked during lifecycle verification, so that documentation CRUD does not leave broken navigation.
66. As a future maintainer, I want canonical definitions for Shaping, Work Contract, Execution Package, Work Unit, Package Approval, Worker Exception, Integration Card, and Legacy Workflow, so that code and documentation share one language.
67. As a future maintainer, I want an architectural decision record for artifact-first execution, so that the removal of Direct Work and Work Size remains understandable.

## Implementation Decisions

- Introduce `workflow_version: 2` as the explicit selector for artifact-first initiatives. A linked version 2 Work Contract selects the new flow. Active cards without one remain legacy version 1 work during migration.
- Replace pre-execution route selection with **Shaping**. Shaping includes brainstorming, feedback, read-only repository investigation, artifact drafting, work splitting, dependency design, and package approval.
- Permit artifact creation before Kanban cards exist. Prohibit product-code mutation, implementation dispatch, and execution commands during Shaping.
- Define **Work Contract** as the initiative authority for objective, boundaries, exclusions, global acceptance, and verification strategy.
- Define **Spec** as the detailed behavior authority for interfaces, rules, edge cases, and constraints.
- Define **Work Unit** as one independently executable unit with one owner, bounded scope, observable acceptance, explicit dependencies, a known workspace, and canonical verification.
- Define **Plan** as the ordered implementation and local verification description for one Work Unit.
- Define **Execution Package** as one approved Work Contract, one approved Spec, the complete Work Unit split, one approved Plan per Work Unit, dependency graph, workspace allocation, verification strategy, and final Integration Card.
- Require one stable user-provided `WORK-KEY` for the initiative and one shaping-time `UNIT-KEY` per Work Unit. Hermes internal task IDs remain runtime identifiers and do not determine artifact names.
- Use repository-local Markdown artifacts. Version 2 does not support externally hosted Work Contracts. External support may be reconsidered later with immutable revisions and reliable retrieval.
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
- Create a dedicated documentation migration Work Unit. It owns creation, reading/auditing, updating, and deletion of all related workflow documentation and diagrams.
- Create a domain glossary containing Shaping, Work Contract, Execution Package, Work Unit, Package Approval, Worker Exception, Integration Card, and Legacy Workflow.
- Record the artifact-first workflow choice in an ADR because it is hard to reverse, surprising without context, and chosen over a materially different size-based alternative.
- Migrate all coupled surfaces in one coordinated release: workflow skill, templates, routing guidance, completion gate, package validator, lifecycle tests, plugin tests, repository overview, architecture documentation, examples, diagrams, and target-project starter guidance.
- Pilot version 2 behind the explicit version marker. Make it default for new initiatives after a successful real pilot. Preserve version 1 only for cards already active at cutover, then remove it after those cards close.

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
- Extend the lifecycle seam to prove active legacy version 1 cards retain old behavior while version 2 packages use artifact-first behavior.
- Add narrow plugin or validator unit tests only for failure cases that are difficult to observe precisely through the lifecycle test. Keep seams minimal.
- Unit-test package rejection for missing artifacts, non-approved states, missing required sections, duplicate keys, broken or mismatched links, cyclic dependencies, missing owners, unsafe concurrent workspace overlap, dirty linked paths, missing commits, and absent baseline verification.
- Unit-test Worker Exception classification and confirm ordinary implementation/test failures are not exceptions.
- Unit-test retry exhaustion thresholds and goal-turn budget enforcement.
- Unit-test card schema validation for Contract, Spec, Plan, dependencies, verification, workspace, assignee, goal mode, and turn budget.
- Preserve prior completion-gate and native review-transition tests as regression coverage for evidence, linked-artifact state, completion baselines, drift, request-changes, and final completion.
- Use existing plugin tests as prior art for deterministic guidance and gate failures.
- Use existing shell integration tests as prior art for command-level startup and setup behavior.
- Make documentation migration testable: scan maintained workflow sources for obsolete version 2 Work Size and Direct Work language, permit legacy terms only in explicitly marked version 1 compatibility sections, and validate references/links through the lifecycle test or one focused documentation check.
- Run canonical repository verification before declaring implementation complete: lint plus full deterministic test suite.

## Out of Scope

- Supporting external or remote Work Contracts in version 2.
- Deriving package approval from chat history without an approved repository artifact and committed baseline.
- Automatic product implementation during Shaping.
- Allowing workers to expand objective, scope, acceptance, dependencies, specified behavior, security boundaries, or verification contracts without reapproval.
- Replacing Hermes Kanban, its native task states, dispatcher, reviewer lifecycle, or notification model.
- Replacing target-project canonical verification with Ginflow validation.
- Creating permanent version 1 compatibility mode for new initiatives.
- Estimating effort through renamed size labels. Turn budgets are runtime bounds, not effort categories.
- Reviewer-authored implementation fixes.
- Completing an initiative based on percentage done or a subset of the original acceptance criteria.
- Reworking unrelated Ginflow tracing or setup behavior unless required by artifact-first lifecycle integration.

## Further Notes

- Canonical flow: `Shaping → Work Contract → Spec → Work Units and Plans → blocked cards → package approval and commit → package validation → root unblocking → goal-mode execution → review → Integration Card → initiative completion`.
- Artifact creation is part of Shaping and occurs before Kanban execution. Product-code mutation starts only after cards exist and the package passes its gate.
- “Run until done or exception” is the central worker design constraint. New prompts or pauses should not be added for decisions already delegated by the approved package.
- The documentation migration is a first-class Work Unit, not cleanup after implementation. Release cannot complete while current and version 2 workflow descriptions conflict.
- Rollout order: implement explicit version 2, run one real pilot initiative, fix package/worker friction, make version 2 default for new work, allow active legacy cards to close, then remove legacy routing.
