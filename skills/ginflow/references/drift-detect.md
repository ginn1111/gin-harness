# Drift detection

Use drift detection at 2 levels.

## 1. Project workflow drift first

Run from target repo.

Example:

```bash
bash scripts/verify.sh
```

Typical checks:
- local docs match task status
- required project files exist
- task artifacts follow local conventions
- local verification commands still exist
- workspace points to correct repo

Purpose:
- prove project workflow still matches project rules

## 2. Global setup drift second

Run from setup repo:

```bash
bash scripts/verify.sh
```

Checks:
- profiles exist
- `SOUL.md` symlinks correct
- generated config uses repo-local paths
- expected memory/provider fields present
- skills available
- `.no-bundled-skills` present
- canonical setup files committed

Purpose:
- prove installed profiles still inherit setup repo correctly

## Rule

Project drift check comes first during real work.
Setup repo drift check is separate and only for profile install health.
