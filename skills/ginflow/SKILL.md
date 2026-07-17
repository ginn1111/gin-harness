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

## Drift detection

Use drift detection in 2 layers, in this order:

1. **Project workflow drift first** — target repo should own its own `verify.sh`
   - checks task artifacts, local conventions, task-vs-doc drift, local verification paths
   - run this first when doing project work
2. **Global setup drift second** — setup repo `scripts/verify.sh`
   - checks deployed profiles still match setup repo
   - checks symlinks, config paths, shared skills, bundled-skill opt-out

Rule:
- target repo drift check comes first during real work
- setup repo `verify.sh` is only for profile installation health
- do not mix them

## Blank project flow

If user starts in blank project:

1. inspect repo for `AGENTS.md` / `.hermes.md`
2. if missing, help create minimum local setup first
3. add build/test/lint/run commands if known
4. add forbidden areas / deploy rules if known
5. if commands are unknown, leave placeholders and mark them missing
6. only then shape first task

Minimum local setup:
- `AGENTS.md` or `.hermes.md`
- install/dev/build/test/lint commands
- key directories
- forbidden/sensitive paths
- definition of done / verification path

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
- `references/drift-detect.md`
- `references/blank-project-checklist.md`
- `templates/brief.md`
- `templates/plan.md`
- `templates/spec.md`
- `templates/kanban-task.md`
- `templates/AGENTS.md`
