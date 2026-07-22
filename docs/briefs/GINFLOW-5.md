---
status: ready
size: XS
scope: Ginflow planning guidance and routing context
owner: gintary
---

# Brief — GINFLOW-5 Load plan skill for Ginflow planning work

## Objective

Require Ginflow agents to load and follow `plan` before creating a plan for planning-required work.

## Scope

- `skills/ginflow/SKILL.md` task-shaping guidance.
- `plugins/ginflow-routing/__init__.py` injected routing context.
- `skills/ginflow/scripts/test-ginflow-routing.py` regression coverage.

## Acceptance criteria

- [ ] Ginflow guidance requires `plan` skill before plan creation when planning is required.
- [ ] Routing context states same requirement while Ginflow is active.
- [ ] Regression test checks injected context for instruction.
- [ ] `make lint` and `make test` pass.

## Non-goals

- Change plan-skill behavior.
- Change Ginflow Kanban lifecycle.

## Notes

Canonical verification: `make test`.
