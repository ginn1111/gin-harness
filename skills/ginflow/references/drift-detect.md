# Drift detection

Use drift detection at 2 levels.

## 1. Global setup drift

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

## 2. Project workflow drift

Optional in target repo.

Typical checks:
- local docs match task status
- required project files exist
- task artifacts follow local conventions
- local verification commands still exist

Purpose:
- prove project workflow still matches project rules

## Rule

Setup repo drift check != project drift check.
Keep them separate.
