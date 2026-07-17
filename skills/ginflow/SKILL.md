---
name: ginflow
description: Use when working under gin global Hermes profiles and deciding how to organize project docs, shape tasks, write Kanban cards, or split setup-repo rules from target-project rules.
---

# ginflow

Global workflow guide shared by installed profiles from setup repo.

## When to use

Use when any of these apply:
- starting work in blank project
- deciding where docs belong
- deciding brief vs spec vs plan
- shaping Kanban task for `ginb`
- explaining setup-repo vs target-repo split

## Core split

- **Setup repo** owns global profiles, shared skills, setup/update scripts
- **Target repo** owns code, tests, local docs, local task artifacts
- **Task workspace** must point at real target repo

Never use setup repo as default code workspace.

## Doc layout

Put these in target repo when project needs them:

| Artifact | Purpose |
|---|---|
| `AGENTS.md` | local project rules, cross-agent portable |
| `.hermes.md` | Hermes-specific project rules |
| `briefs/DM-XX.md` | concrete task brief |
| `specs/` | behavior/contract detail when needed |
| `plans/` | execution order for medium+ work |
| `adrs/` | durable architectural decisions |

Starter local context:
- copy `templates/AGENTS.md` from setup repo into target repo

## Task shaping

### Choose work mode

1. **Investigation** — cause unclear
2. **Implementation** — requirement clear
3. **Brainstorming** — requirement unclear

### Choose artifact level

| Case | Brief | Spec | Plan |
|---|---:|---:|---:|
| XS/S clear work | yes | optional | optional |
| M work | yes | optional | yes |
| L/XL or risky work | yes | yes | yes |
| Investigation | yes | optional | yes |
| Brainstorming | note first | later | later |

Rule:
- brief always
- spec when behavior/contract can drift
- plan when ordering/risk matters

## Kanban card shape

Keep card thin.

Include only:
- objective
- scope
- acceptance criteria
- link to project artifact if present

Use real target repo workspace:
- `--workspace dir:/abs/path/to/project`
- `--workspace worktree` for isolated git changes

## Required fields for build-ready handoff

A task for `ginb` should answer:
- what to change
- where to change it
- how done is judged
- what not to touch

If any missing and risk is material, block back to `gintary`.

## Blank project flow

1. create or copy `AGENTS.md`
2. add build/test commands
3. add forbidden areas / deploy rules
4. then shape first task

## Stop rules

Stop and clarify when:
- wrong repo
- fuzzy requirement
- unclear cause but user expects direct fix
- acceptance criteria missing
- no verification path

## References

- `references/doc-layout.md`
- `references/kanban-guide.md`
- `templates/brief.md`
- `templates/plan.md`
- `templates/spec.md`
- `templates/kanban-task.md`
- `templates/AGENTS.md`
