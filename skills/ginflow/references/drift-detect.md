# Verification separation

Use three separate checks. Never merge their meaning.

## 1. Project verification

Run exact canonical command declared by target repo from target root, for example:

```bash
make verify
```

Target may instead declare `./verify.sh` or another project-native command. Ginflow does not force script name or location.

Purpose:
- prove project behavior matches project rules
- block completion when command fails or is unavailable

## 2. Ginflow harness

Run harness from setup repo or deployed ginflow skill against target repo and selected Kanban card. Never copy harness script into target repo, add it to target dependencies, or include it in project verification.

Purpose:
- detect workflow readiness and drift
- report result separately from project verification
- block affected lifecycle stage for missing card, wrong workspace, missing acceptance, missing required artifact, or missing completion verification path
- report other drift as warning

Harness unavailable is a warning and never substitutes for project verification.

## 3. Global setup verification

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

## Report shape

```text
Project verification: pass|fail|blocked
Ginflow harness: pass|warning|blocker|unavailable
Profile installation: pass|fail|not-run
```

Project verification comes first during real work. Ginflow harness remains external. Setup verification only checks profile installation health.
