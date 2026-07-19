# APP-8 completion workflow

Do not copy `validate-harness.py` into target repo or add it to `make check`. Harness belongs to setup/deployed ginflow skill. Target repo keeps project-native verification independent.

1. From target repo root, run canonical project verification first:

   ```bash
   make check
   ```

   Failure or unavailable command blocks APP-8 completion. Record exact fresh output/result on APP-8.

2. Inspect target-repo scope evidence:

   ```bash
   git status --short
   git diff --stat
   ```

   Confirm changed files stay within APP-8 scope. Do not modify repo for harness integration.

3. From setup repo, run harness externally against real target and selected card:

   ```bash
   python3 /home/aioz/personal/agents-hype/skills/ginflow/scripts/validate-harness.py \
     --setup-repo /home/aioz/personal/agents-hype \
     --target /absolute/path/to/target-repo \
     --card /absolute/path/to/APP-8-card.json
   ```

   Substitute actual target and selected-card paths. Harness never becomes target dependency and never substitutes for `make check`.

4. Report results separately and record same evidence on APP-8 before completion:

   ```text
   Project verification: pass|fail|blocked — `make check`; exact fresh result
   Ginflow harness: pass|warning|blocker|unavailable — external command; exact fresh result
   Profile installation: not-run
   Changed files: target `git status --short` result
   ```

`make check` failure blocks completion. Harness missing/unavailable is warning. General harness drift is warning. Missing card, wrong workspace, missing acceptance, missing required artifact, or missing completion verification path is blocker for affected lifecycle stage. Since APP-8 is complete, keep status complete only when canonical verification passes, scope evidence is valid, required card evidence is recorded, and harness finds no completion-stage blocker.
