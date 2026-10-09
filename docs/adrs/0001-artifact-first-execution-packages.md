---
status: completed
size: M
scope: Ginflow v2 artifact-first execution
owner: gin
---

# ADR 0001: Artifact-first execution packages

## Decision

Ginflow v2 uses one repository-local, approved Execution Package before implementation dispatch. Package contains Work Contract, Spec, Work Units, one Plan per unit, dependency graph, workspace allocation, verification strategy, and Integration Card. Package selects workflow with `workflow_version: 2`.

Shaping owns brainstorming, feedback, read-only investigation, artifact drafting, splitting, and one final approval. Cards are created blocked, then share one committed package baseline. A deterministic validator must pass before root cards unblock. Integration combines Work Units but does not complete its Initiative; successful Integration opens the read-only human Decision phase, and `approved_for_mr` completes Ginflow lifecycle.

Initiative, Execution Batch, Review Cycle, Decision Projection, Notification, and MR Intent are additive provider-neutral contracts. Hermes remains lifecycle authority; target repositories remain product and canonical-verification authority.

TUI, direct Hermes database access, gateway transport/subscription setup, and provider-specific merge-request publication remain deferred.

Active version 1 cards keep legacy behavior during migration. New v2 work does not use Work Size, Direct Work, or size-based routing.

## Context

Size-based routing permits incomplete scope and subjective execution decisions. Mid-task clarification interrupts workers and weakens auditability. Artifact-first preparation moves decisions before dispatch while retaining Hermes Kanban as lifecycle authority and project-native verification as behavior evidence.

## Trade-offs

- More up-front shaping and artifact maintenance.
- Local Markdown artifacts require repository access; remote contracts stay out of v2.
- Stable human keys improve links, but require key validation before Hermes task IDs exist.
- One package baseline improves reproducibility, but package revisions require reapproval and revalidation.
- Explicit v1 compatibility adds migration logic temporarily, but avoids invalidating active work.

## Rejected alternative

Keep XS/S/M/L/XL routing and select Spec/Plan conditionally. This keeps startup small, but preserves subjective routing and lets incomplete work reach workers.
