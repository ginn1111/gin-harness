# ADR-001 — Hybrid Kanban + Markdown Delivery Pipeline

**Date:** 2026-07-18
**Status:** accepted

## Context

Gin delivery pipeline (gintary → ginb → done) was pure Kanban. Kanban carried specs, plans, delivery summaries inside task bodies + metadata. Problems:

- No permanent git-trackable record of what was delivered
- Cross-task linking via backlinks impossible
- Human browsing required kanban dashboard instead of repo
- No diff/review on spec changes
- Drift between kanban status and actual delivery state

## Decision

**Kanban owns active routing status. .md files own everything else.**

### Split

| Owned by kanban | Owned by .md files |
|----------------|-------------------|
| Status (ready/running/blocked/done) | Brief, spec, plan |
| Task ID | Implementation detail |
| Parent/child links | Decisions (ADRs) |
| Assignee | Delivery summary |
| Block reason | Changed files, test results |
| Heartbeats | Backlinks `[[DM-42]]` |
| Artifact delivery | Git history |
| Git SHAs (md_sha_at_*) | |
| Audit trail (event log) | |

### Flow

1. **gintary**: writes `briefs/DM-XX.md` → `git commit` → records SHA → creates thin kanban card with `md_sha_at_create`
2. **ginb**: reads card → follows link to .md → implements → writes delivery summary to .md → `git commit` → records SHA in `kanban_complete(metadata={md_sha_at_complete: SHA})`
3. **gintary**: runs `verify.sh` after completion to detect status drift + content drift
4. **verify.sh**: compares kanban status vs .md `status:` frontmatter, compares .md SHA at last transition vs current HEAD

### Drift detection

- **Status drift**: kanban status ≠ .md frontmatter `status:` field (skip `running` = expected mismatch)
- **Content drift**: .md changed after delivery closed (`md_sha_at_complete` ≠ current HEAD SHA for that file)

## Consequences

+ Full git history of every delivery spec and summary
+ Cross-task backlinks in plain markdown
+ Human browses repo, not just dashboard
+ Diff/review on spec changes
+ Drift detection catches silent edits
+ Thin kanban cards (less noise in board)

- Need to keep .md frontmatter `status:` in sync (enforced by ginb + verify.sh)
- Extra git commit on every terminal transition (minor overhead)
- Hybrid adds complexity vs pure kanban or pure markdown

## Related

- [[ginb.SOUL.md]]
- [[gintary.SOUL.md]]
- [[verify.sh]]
