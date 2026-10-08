# Ginflow glossary

- **Initiative** — stable aggregate identity linking Discovery, approved package revisions, Execution Batches, cards, Review Cycles, notifications, and merge-request intents.
- **Discovery** — read-only problem framing: desired outcome, constraints, non-goals, prototype evidence, vocabulary, and open questions.
- **Shaping handoff** — approved Discovery output that authorizes Shaping to form one Execution Package.
- **Execution Package** — artifact-first Ginflow v2 contract containing approved contract/spec, Tickets, plans, dependencies, workspaces, and baseline verification.
- **Execution Batch** — immutable AFK attempt bound to one package digest, artifact baseline, Ticket set, workspaces, budget, stop conditions, and actor authorization.
- **Work Unit** — one Ticket execution card. Parallel mutation requires isolated worktrees or workspaces.
- **Integration** — dedicated card and terminal outcome that combines Work Units and verifies the result. Success opens Decision; it does not complete Initiative.
- **Change Group** — behavior-oriented review unit mapping Tickets, acceptance, and changed paths.
- **Decision** — read-only human context recovery and disposition phase after successful or blocked Integration.
- **Review Cycle** — append-only evidence, findings, dispositions, and aggregate Decision revision bound to exact commits and actors.
- **Decision Projection** — bounded, redacted `decision_projection/v1` structured view for future TUI consumers; it is not workflow authority.
- **Notification** — gateway-ready `notification/v1` envelope for material outcomes, with idempotency and delivery state; transport remains adapter-owned.
- **MR Intent** — provider-neutral `merge_request_intent/v1` preview containing exact refs/commits, lineage, review digest, checks, risks, reviewers, labels, draft state, and publication status.
- **Prototype promotion** — explicit production coverage for prototype evidence through Spec, Plan, Ticket, acceptance, and verification; prototype code is non-production by default.

## Authority boundaries

Hermes remains identity, Kanban, assignment, dispatch, lifecycle, and persistence authority. Ginflow core validates pure records and derives projections. Adapters collect Git/check evidence, deliver notifications, and later publish provider-specific merge requests. Target repositories remain authority for product behavior and canonical verification. TUI, direct Hermes database access, gateway transport/subscriptions, and provider publication remain deferred.
