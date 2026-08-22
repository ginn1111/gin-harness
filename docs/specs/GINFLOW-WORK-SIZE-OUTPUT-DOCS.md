# Ginflow Direct Work, Governed Work, and Routing Guidance

## Problem Statement

Ginflow currently assumes that build-ready repository work is controlled by a Kanban Card. That protects Governed Work, but it adds disproportionate lifecycle and Governance Artifact overhead to genuinely tiny, clear, reversible changes. Existing routing guidance also mixes work mode, Work Size, artifact selection, and skill loading without a single explicit contract, and it can imply semantic classification or plugin-owned orchestration that the system does not provide.

Users need Ginflow to distinguish safe Direct Work from Governed Work without weakening fail-closed behavior. They also need unresolved facts to enter Clarification rather than being interpreted as safety or causing premature cards and artifacts. The resulting route must use consistent domain language, deterministic output precedence, explicit `skill_view` guidance, canonical verification, and evidence-based completion.

Existing lifecycle feedback is card-scoped and fragmented across gate, blocker, recovery, verification, and completion behavior. Governed Work needs a small normalized feedback contract without introducing telemetry, analytics, persistence, or a new orchestration service.

## Solution

Ginflow will expose three routing outcomes:

- **Direct Work** when every Direct Work Eligibility factor is affirmatively established.
- **Governed Work** when a known disqualifier exists, including M/L/XL Work Size, Risk Impact, Governance Artifact need, or conflicting workspace ownership.
- **Clarification** when any required fact is unknown. Clarification permits conversation-led brainstorming and Read-only Investigation, but no repository mutation, Kanban Card, or Governance Artifact.

Eligible Direct Work is limited to clear XS/S implementation with known target behavior, known bug root cause when repairing a defect, localized and reversible scope, no Risk Impact, no Governance Artifact requirement, known canonical verification, project-local permission, and an unowned single-worker workspace. Direct Work produces a Delivery Change, canonical verification evidence, scoped diff review, and a conversation result. It creates no card, `Links` field, marker, temporary execution record, Spec, Plan, ADR, Wayfinder, or Handoff.

Known-ineligible work uses Governed Work. Its Kanban Card remains the authority for objective, included and excluded scope, acceptance, work mode, Work Size, size rationale, workspace, assignee, status, links, and progress. Spec and Plan remain conditional Governance Artifacts selected by behavior/contract and ordering/verification needs. Brief is removed universally.

The Ginflow gate will inject deterministic route, output, escalation, and bounded skill guidance. Hermes—not the plugin—will evaluate advisory Direct Work Eligibility and call `skill_view`. A selected skill must follow Ginflow’s route/output contract; a skill’s default document location does not independently disqualify Direct Work or create a competing Governance Artifact.

Feedback v1 will normalize Governed Work lifecycle events only. It will remain card-scoped because current verification, gate, blocker, recovery, and completion signals all have stable card identity. Direct Work feedback events are deferred until a stable non-card identity contract exists.

## User Stories

1. As a Ginflow user, I want tiny safe changes to avoid Kanban overhead, so that governance remains proportional to risk and complexity.
2. As a Ginflow user, I want eligible XS/S implementation to use Direct Work, so that a small Delivery Change can be completed efficiently.
3. As a Ginflow user, I want Direct Work Eligibility to be affirmatively established, so that missing information is never mistaken for safety.
4. As a Ginflow user, I want an unknown eligibility factor to enter Clarification, so that the system does not guess a route.
5. As a Ginflow user, I want known Direct Work disqualifiers to route to Governed Work, so that risky or complex work receives lifecycle controls.
6. As a Ginflow user, I want unclear requirements to remain in Clarification, so that no premature card or implementation is created.
7. As a Ginflow user, I want Read-only Investigation during Clarification, so that an agent can establish facts without mutating project state.
8. As a Ginflow user, I want Read-only Investigation to rerun routing after facts are known, so that investigation does not silently become implementation.
9. As a Ginflow user, I want Direct Work limited to implementation with clear target behavior, so that ambiguous design work cannot bypass governance.
10. As a Ginflow user, I want a defect’s root cause known before Direct Work repair begins, so that speculative fixes do not use the small-work route.
11. As a Ginflow user, I want Work Size based on components, owners, contracts, ordering, operational concerns, verification, and split needs, so that sizing reflects actual complexity.
12. As a Ginflow user, I want raw file count excluded as standalone Work Size evidence, so that mechanical multi-file changes are not automatically oversized.
13. As a Ginflow user, I want title wording and word count excluded from Work Size inference, so that labels do not replace shaping.
14. As a Ginflow user, I want semantic similarity excluded from Work Size inference, so that routing remains deterministic and explainable.
15. As a Ginflow user, I want Risk Impact based on credible behavior or control effects, so that risky keywords alone do not force Governed Work.
16. As a Ginflow user, I want actual security or privacy impact to force Governed Work, so that sensitive changes receive explicit controls.
17. As a Ginflow user, I want actual data, migration, or concurrency impact to force Governed Work, so that state and consistency risks are governed.
18. As a Ginflow user, I want actual deployment, compatibility, or difficult-rollback impact to force Governed Work, so that operational risk is explicit.
19. As a Ginflow user, I want Direct Work to require localized and reversible scope, so that recovery remains straightforward.
20. As a Ginflow user, I want Direct Work to require known canonical verification, so that completion is evidence-based.
21. As a Ginflow user, I want Direct Work blocked when a selected or running card owns the workspace, so that concurrent lifecycle authority is not bypassed.
22. As a Ginflow user, I want Direct Work blocked when another worker mutates the workspace, so that changes do not race.
23. As a Ginflow user, I want unknown workspace ownership to enter Clarification, so that uncertainty is not treated as an available workspace.
24. As a Ginflow user, I want Direct Work to create no Kanban Card, so that the route does not recreate governed overhead.
25. As a Ginflow user, I want Direct Work to create no replacement marker or temporary execution record, so that it does not introduce a second lifecycle system.
26. As a Ginflow user, I want Direct Work to create no Governance Artifact, so that its output remains the Delivery Change and conversation result.
27. As a Ginflow user, I want implementation files distinguished from Governance Artifacts, so that persistent code or documentation does not automatically disqualify Direct Work.
28. As a Ginflow user, I want Direct Work to declare work mode, Work Size, route identifier, rationale, output contract, and verification, so that the decision is inspectable.
29. As a Ginflow user, I want Direct Work completion to report changed files, exact verification, scoped diff review, and limitations, so that the result is auditable without a card.
30. As a Ginflow user, I want failed local verification to permit repair only while Direct Work Eligibility remains true, so that local iteration remains proportionate.
31. As a Ginflow user, I want expanded scope or newly discovered Risk Impact to stop Direct Work immediately, so that the agent cannot silently broaden the route.
32. As a Ginflow user, I want stopped Direct Work to reroute to Clarification or Governed Work, so that the next state matches the discovered facts.
33. As a Ginflow user, I want M/L/XL work to use Governed Work, so that coordinated and cross-cutting changes have explicit authority.
34. As a Ginflow user, I want a Governed Work card to record Work Size and size rationale, so that the governance choice is explainable.
35. As a Ginflow user, I want exclusions represented inside card scope, so that separate and conflicting non-goal fields are unnecessary.
36. As a Ginflow user, I want Spec selected only when behavior or contracts can drift, so that specifications remain purposeful.
37. As a Ginflow user, I want Plan selected when ordering, investigation, rollback, or layered verification matters, so that execution dependencies are explicit.
38. As a Ginflow user, I want ADR used only for durable architectural trade-offs, so that routine work does not create decision noise.
39. As a Ginflow user, I want Handoff used only as an optional resume snapshot, so that it does not become an authority document.
40. As a Ginflow user, I want Brief removed from every route, so that authority is not duplicated.
41. As a Ginflow user, I want `Links: - none` valid only on an existing Governed Work card, so that a card sentinel is not applied to Direct Work.
42. As a Ginflow user, I want project-local rules to have highest output precedence, so that target-project policy remains authoritative.
43. As a Ginflow user, I want explicit route or card output contracts to outrank general Ginflow defaults, so that shaped work remains deterministic.
44. As a Ginflow user, I want Ginflow’s Work Size/output matrix to outrank skill defaults, so that skills do not create competing authorities.
45. As a Ginflow user, I want selected skills to retain their methods and quality criteria, so that routing does not erase specialist guidance.
46. As a Ginflow user, I want a skill’s default folder treated as a fallback, so that packaging conventions do not control governance.
47. As a Ginflow user, I want Hermes to call `skill_view`, so that the plugin does not emulate or bypass the skill system.
48. As a Ginflow user, I want the plugin to inject bounded candidate skill guidance, so that skill selection remains explicit without semantic search.
49. As a Ginflow user, I want the plugin to avoid arbitrary prose classification, so that routing behavior remains deterministic.
50. As a Ginflow user, I want the plugin to avoid creating cards or Governance Artifacts, so that ownership remains with Hermes and workers.
51. As a Ginflow user, I want the plugin to avoid Kanban mutation, so that routing guidance does not become orchestration.
52. As a Ginflow user, I want existing Governed Work routes to remain fail-closed, so that the new route does not weaken current safety.
53. As a Ginflow user, I want invalid card metadata routed to repair or blocking, so that it is not confused with technical investigation.
54. As a Ginflow user, I want the architecture diagram to use Direct Work, Governed Work, and Clarification consistently, so that the design reflects the domain glossary.
55. As a Ginflow user, I want `direct-no-card` shown only as a machine-facing identifier, so that implementation vocabulary does not replace domain language.
56. As a Ginflow user, I want architecture colors to distinguish verified Governed Work from proposed Direct Work, so that implementation status is visible.
57. As a Ginflow maintainer, I want one high-level routing seam to test injected behavior, so that tests observe the contract rather than helper internals.
58. As a Ginflow maintainer, I want real temporary workspace and Kanban context in routing tests, so that integration behavior is exercised realistically.
59. As a Ginflow maintainer, I want tests for all three routing outcomes, so that pass, known failure, and unknown states cannot collapse together.
60. As a Ginflow maintainer, I want tests proving risky keywords do not equal Risk Impact, so that routing avoids false positives.
61. As a Ginflow maintainer, I want tests proving raw file count does not determine Work Size, so that sizing remains structured.
62. As a Ginflow maintainer, I want tests proving Direct Work creates no card, marker, record, or Governance Artifact, so that the advisory route has no hidden mutation.
63. As a Ginflow maintainer, I want tests proving scope expansion emits stop-and-reroute guidance, so that Direct Work cannot silently drift.
64. As a Ginflow maintainer, I want Governed Work feedback normalized through a pure builder, so that lifecycle signals share one bounded contract.
65. As a Ginflow maintainer, I want feedback v1 to use stable card identity, so that every event has a trustworthy reference.
66. As a Ginflow maintainer, I want unsupported feedback values rejected, so that downstream consumers receive predictable data.
67. As a Ginflow maintainer, I want feedback construction to avoid filesystem, process, notification, and Kanban mutation, so that the contract remains pure.
68. As a Ginflow maintainer, I want Direct Work feedback deferred, so that the system does not invent an unstable non-card identity.
69. As a Ginflow maintainer, I want repository-native lint and tests to verify the complete change, so that delivery follows project norms.
70. As a Ginflow maintainer, I want unrelated working-tree changes preserved, so that implementation remains scoped.

## Implementation Decisions

- The domain uses Direct Work, Governed Work, Clarification, Direct Work Eligibility, Read-only Investigation, Work Size, Risk Impact, Governance Artifact, and Delivery Change as canonical terms.
- `direct-no-card` is a machine-facing route identifier, not the user-facing domain term.
- Routing has exactly three outcomes: affirmative pass, known failure, and unknown.
- Direct Work Eligibility is advisory and agent-evaluated. No marker, temporary authorization record, or mini-card will be introduced.
- Every Direct Work Eligibility factor must be affirmatively established. Absence of evidence is not evidence of safety.
- Clarification permits conversation-led brainstorming and Read-only Investigation. It prohibits repository mutation, card creation, Governance Artifact creation, and implementation.
- Work Size uses requirement clarity, cause/target clarity, affected components and owners, behavior/contract impact, ordering, operational concerns, verification layers, and split needs.
- Raw file count, title wording, word count, and semantic similarity are prohibited as standalone Work Size classifiers.
- Risk Impact represents credible behavior or control impact. Keyword matching is not a risk classifier.
- Direct Work requires genuine XS/S size, clear target behavior, known bug root cause for repair, localized reversible scope, no Risk Impact, no Governance Artifact need, known canonical verification, project-local permission, and exclusive mutable workspace ownership.
- Direct Work creates a Delivery Change and conversation result only. It creates no card, `Links`, Brief, Spec, Plan, ADR, Wayfinder, Handoff, marker, or temporary execution record.
- A repository-persistent implementation or project-documentation change is a Delivery Change, not automatically a Governance Artifact.
- Direct Work may repair a failed verification only while all eligibility factors remain true.
- Scope expansion, ambiguity, wider impact, Risk Impact, ownership conflict, or unknown verification stops Direct Work before further mutation and triggers rerouting.
- Governed Work requires a build-ready Kanban Card. The card owns objective, scope inclusions and exclusions, acceptance, work mode, Work Size, size rationale, workspace, status, assignee, links, and progress.
- Brief is removed universally.
- Spec is conditional on behavior, contract, state, compatibility, data, or failure-semantic drift.
- Plan is conditional on ordering, investigation, rollback, coordination, or layered verification.
- ADR and Handoff remain optional and purpose-driven rather than size-driven.
- `Links: - none` is a sentinel only for an existing Governed Work card with no Governance Artifact.
- Canonical output precedence is project-local rules, explicit route/card output contract, Ginflow matrix, selected skill instructions, then skill default location.
- A skill’s default document preference does not independently disqualify Direct Work. Skills adapt their method to the selected Ginflow output contract.
- The Ginflow gate injects deterministic route, output, escalation, and bounded skill guidance through the existing pre-model-call integration point.
- Hermes calls `skill_view`; the plugin never calls or emulates the tool.
- The plugin does not inspect skill folders, create cards or Governance Artifacts, mutate Kanban state, or perform semantic similarity search.
- Existing workspace, explicit-task, status, validation, blocked, and terminal Governed Work routes remain compatible and fail-closed.
- Feedback v1 is restricted to Governed Work and uses stable card identity.
- Feedback v1 normalizes existing verification, gate, blocker, recovery, correction, and completion signals through a pure validated builder.
- Feedback v1 does not persist events, notify users, mutate cards, query analytics, or drive hidden routing mutation.
- Direct Work feedback is deferred until a stable non-card identity contract is designed.
- The architecture flow page will adopt canonical domain terminology and the three-outcome routing model while preserving the unrelated overview page.

## Testing Decisions

- Tests will assert externally visible behavior instead of private helper structure, formatting implementation, or constant layout.
- The primary seam is the existing pre-model-call routing context exercised through the Ginflow gate’s high-level routing test.
- Primary-seam tests will use real temporary workspace and Kanban context where existing prior art already does so.
- Primary-seam tests will cover Direct Work, Governed Work, and Clarification outcomes; route rationale; canonical output contract; bounded candidate skill; explicit `skill_view` instruction; and mandatory stop/reroute guidance.
- Primary-seam tests will verify that unknown facts enter Clarification rather than Direct Work or automatic Governed Work.
- Primary-seam tests will verify that actual Risk Impact disqualifies Direct Work while risky vocabulary without impact does not.
- Primary-seam tests will verify that raw file count, title wording, and semantic similarity are not Work Size classifiers.
- Primary-seam tests will verify that selected/running workspace cards and concurrent mutators disqualify Direct Work, while unknown ownership enters Clarification.
- Primary-seam tests will verify that Direct Work guidance creates no card, `Links`, marker, temporary record, Governance Artifact, or Kanban mutation.
- Primary-seam tests will verify that scope, clarity, ownership, verification, or Risk Impact changes produce stop-and-reroute guidance.
- Existing workspace/status and temporary-project/card routing tests are the prior art for the primary seam.
- The secondary seam is the public Governed Work feedback-event builder.
- Secondary-seam tests will validate supported signals, results, next actions, stable card identity, timestamps, single-line safe reason fields, and evidence references.
- Secondary-seam tests will reject missing fields, unsupported values, malformed timestamps, unsafe multiline values, and invalid identifiers.
- Secondary-seam tests will prove fresh-return and no-mutation behavior for inputs, filesystem, processes, notifications, and Kanban state.
- Existing blocker-event and recovery-policy contract tests are the prior art for the secondary seam.
- Direct Work feedback tests are intentionally absent from v1 because no stable non-card identity contract exists.
- Repository-native lint, focused plugin tests, complete plugin tests, XML parsing, Draw.io structural validation, and the canonical full test command will provide final verification.

## Out of Scope

- Semantic classification from arbitrary task prose.
- Similarity-based skill discovery or unrestricted skill recommendation.
- Plugin-owned `skill_view` calls or skill-content inspection.
- Plugin-created Kanban Cards, Governance Artifacts, markers, or temporary execution records.
- A second orchestration or authorization state machine.
- Brief artifacts.
- Observability, telemetry infrastructure, metrics, traces, dashboards, analytics, or ML feedback loops.
- Feedback persistence, query services, notification delivery, or hidden routing mutation.
- Direct Work feedback events or a non-card identity scheme.
- Full orchestrator runtime ownership.
- Formal security/privacy governance systems or threat-model work.
- Deployment, production mutation, profile configuration changes, or remote git operations beyond publishing this specification issue.
- Normalizing skill package or folder structures.
- Changing the unrelated architecture overview page.

## Further Notes

The architecture flow page was aligned first and validated as parseable Draw.io XML. A final diagram consistency task remains because the subsequently approved domain glossary replaces user-facing “fast path” and “direct-no-card” language with Direct Work, Governed Work, and Clarification.

The local domain glossary is authoritative for terminology. No ADR has been created; the current decisions are captured by this specification and glossary.

Publication target: the project issue tracker with the `ready-for-agent` label.
