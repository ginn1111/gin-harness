# Wayfinder Map — Ginflow Work-Size and Output-Document Guidance

## Destination

A handoff-ready, implementation-ready spec and decision map for deterministic Ginflow work-size evaluation, output-document selection, `skill_view`-based skill guidance, feedback boundaries, and aligned architecture documentation.

## Notes

Domain: Ginflow task shaping, `ginflow-gate` routing, Hermes skills, output artifacts, and lifecycle feedback.
Consult: `ginflow`, `ginflow-gate`, `grilling`, `domain-modeling`, `verification-before-completion`.
Planning only. No implementation in this map.

## Decisions so far

- [Ginflow work-size/output-documents spec](../specs/GINFLOW-WORK-SIZE-OUTPUT-DOCS.md) — proposed solution, user stories, seams, and initial matrix captured; external publication is unavailable.
- [Ginflow routing and feedback plan](../../.hermes/plans/2026-08-16_171036-ginflow-routing-feedback.md) — architecture diagram must align first, followed by routing, feedback, and documentation work.

## Not yet specified

- Canonical source and representation for explicit work size and size rationale.
- Exact precedence rules when work mode, size, risk, and investigation status conflict.
- Exact injected routing-context contract for skill and document guidance.
- Whether the feedback contract remains plugin-owned or becomes reusable core-owned policy.
- Final architecture-diagram labels and page-preservation boundary.
- Completion evidence and card/artifact lifecycle for the implementation handoff.

## Out of scope

- Observability, telemetry, metrics, traces, dashboards, and analytics.
- Full orchestrator runtime or automatic card mutation/splitting.
- Formal security/privacy subsystem.
- LLM semantic classifier, similarity search, and arbitrary dynamic skill selection.
- Direct plugin invocation of `skill_view` or automatic artifact creation.
- Deployment, production mutation, profile identity, secrets, and remote git operations.

## Child tickets

- [Choose the canonical source for work size and rationale](GINFLOW-WORK-SIZE-OUTPUT-DOCS-01.md) — `wayfinder:grilling`
- [Resolve work-size precedence and classification rules](GINFLOW-WORK-SIZE-OUTPUT-DOCS-02.md) — `wayfinder:grilling`
- [Define the injected routing guidance contract](GINFLOW-WORK-SIZE-OUTPUT-DOCS-03.md) — `wayfinder:grilling`
- [Choose feedback contract ownership boundary](GINFLOW-WORK-SIZE-OUTPUT-DOCS-04.md) — `wayfinder:grilling`
- [Align architecture diagram vocabulary and coverage](GINFLOW-WORK-SIZE-OUTPUT-DOCS-05.md) — `wayfinder:prototype`
- [Define implementation handoff and verification evidence](GINFLOW-WORK-SIZE-OUTPUT-DOCS-06.md) — `wayfinder:grilling`

Blocking order: ticket 01 first; ticket 02 depends on 01; ticket 03 depends on 01 and 02; ticket 04 can proceed independently; ticket 05 depends on 02 and 03; ticket 06 depends on 03, 04, and 05.

Status: map charted; no ticket resolved in this session.

Tracker publication remains unavailable because no external issue-tracker integration is configured. These local Markdown files are canonical until tracker integration exists.
