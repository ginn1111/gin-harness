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
