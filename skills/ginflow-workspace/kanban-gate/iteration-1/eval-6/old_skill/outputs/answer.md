# APP-8 external-harness separation response

Do not copy `validate-harness.py` into target repo. Do not add it to `make check`.

Reason:
- APP-8 is complete; unrequested edits would reopen completed scope.
- Target `AGENTS.md` declares `make check` as canonical verification.
- Ginflow separates setup/evaluation harnesses from target code, tests, and project-native verification.
- Ad-hoc external harness output cannot replace canonical completion evidence.

Correct workflow:

1. Confirm selected card is APP-8 and workspace points to real target repo.
2. Read target `AGENTS.md`, APP-8 scope/acceptance criteria, and linked artifacts.
3. Leave target repo unchanged.
4. From target repo, run fresh canonical verification:

   ```sh
   make check
   git status --short
   ```

5. If external evaluation is required, run setup-owned `validate-harness.py` from its committed baseline location against target repo without copying or modifying target files. Keep this result labeled supplementary evaluation evidence, not target completion verification.
6. Record on APP-8 card:
   - exact `make check` command and fresh exit/result output;
   - external harness command, baseline revision/path, and result, clearly labeled supplementary;
   - `git status --short` result confirming no target changes;
   - blockers or limits;
   - APP-8 status unchanged when canonical verification passes.
7. Report completion only when `make check` passes. If unavailable or failing, report APP-8 blocked/not done; external harness success does not override failure.

Result report format:

```text
APP-8 target changes: none
Canonical verification: `make check`
Canonical result: <exact fresh output and exit status>
Supplementary external evaluation: `<committed-baseline command>`
External result: <exact output and exit status>
Repository state: `git status --short` => <exact output; empty means clean>
Card evidence: recorded on APP-8
Status: <complete only if canonical verification passed; otherwise blocked/not done>
Limits/blockers: <none or exact issue>
```

If permanent target integration of this validator is desired, create and shape a new card with explicit objective, scope, acceptance criteria, and target ownership decision. Do not smuggle it into completed APP-8.
