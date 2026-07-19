# Workspace health warnings

Review target workspace immediately before completion. Report findings under `Workspace warnings` on Kanban card and in completion report.

## Decision rule

Warnings do not block completion by default. Promote a finding to blocker only when it affects acceptance, canonical verification, security, privacy, data integrity, or restartability.

For each finding, record:
- severity: warning or blocker
- concrete path or code evidence without exposing secret values
- affected completion condition
- smallest next action

Use `Workspace warnings: none` when review finds nothing. Do not invent findings.

## Review areas

- **Missing runtime config contract** — code reads config absent from committed examples or docs. Keep as warning when safe defaults preserve startup and acceptance; block when deployment or restart can fail.
- **Secret or privacy exposure** — tracked credential files or credible sensitive data are blockers. Never print values. Require safe removal and authorized rotation or review.
- **Unrelated workspace changes** — preserve and report out-of-scope edits. Keep as warning when card work neither reads nor overwrites them and evidence remains clear.
- **Error suppression anti-pattern** — broad catches, ignored failures, or success state after failed external work. Block when acceptance or data integrity can be false.
- **Manifest/generated drift** — block only when build, runtime, verification, or restartability is affected.
- **Debug residue and unresolved TODOs** — warn unless they affect scoped behavior or completion conditions.

Do not copy this policy into target repo. Do not add scanner or policy files there. Use project-native tools and direct inspection; suggest follow-up work only when worthwhile.
