# Safe completion sequence for `t_cd34`

Use one immutable baseline object from validation through completion. Do not complete first and add hashes later, and do not silently re-baseline a completed card.

1. **Read and validate the live card.** Fetch `t_cd34` with `kanban_get` and require its ID, title, objective, scope, acceptance, real target workspace, status, assignee, and links. Resolve only target-local linked artifact paths under that workspace. Stop for a missing card, wrong workspace, missing required field, missing linked file, or link escaping the target repository.

2. **Run fresh project completion checks first.** From the target-repository root, run the canonical verification command declared by `AGENTS.md` or `.hermes.md`; it must pass. Capture the exact command and fresh result, then inspect `git status --short` (and `git diff --stat` when useful). Record that evidence for the completion call. Project verification and Ginflow-harness verification remain separate results.

3. **Build one candidate baseline from the committed artifacts at `COMMIT`.** For every target-local linked document, confirm that the path exists as a regular file in `COMMIT`, hash the exact committed bytes with SHA-256 (for example, `git show COMMIT:<path> | sha256sum`), and construct one path-to-hash map:

   ```json
   {
     "docs/briefs/t_cd34.md": "<sha256-of-COMMIT:docs/briefs/t_cd34.md>",
     "docs/plans/t_cd34.md": "<sha256-of-COMMIT:docs/plans/t_cd34.md>"
   }
   ```

   The paths above are illustrative; use every actual target-local link from the card. Also hash each current working-tree file and require it to equal the corresponding candidate hash. This prevents validating bytes from `COMMIT` while closing over different bytes in the workspace. Keep this map unchanged in a variable such as `BASELINE`.

4. **Validate the exact candidate before closure.** Create a temporary card snapshot from the freshly fetched card, set its candidate status to `completed`, and set its top-level `artifact_baseline` to `BASELINE`. Run the external Ginflow harness against the real target repository and that candidate snapshot; never copy the harness into the target repository or add it to project verification. A completion-stage harness blocker—especially a missing baseline entry, missing artifact, hash mismatch, wrong workspace, missing acceptance, or missing verification path—aborts completion. Report non-blocking warnings separately.

5. **Close atomically with the same object.** Immediately before calling `kanban_complete`, recheck that every current linked file still hashes to `BASELINE`; abort if any value changed. Then make the single completion call and include the unchanged map in completion metadata, together with the fresh completion evidence:

   ```text
   kanban_complete(
     task_id="t_cd34",
     ...completion summary and fresh verification evidence...,
     completion_metadata={
       "artifact_baseline": BASELINE
     }
   )
   ```

   Do not issue a status-only completion followed by a metadata update. The `artifact_baseline` passed to `kanban_complete` must be the exact same path/hash object that the candidate harness validated.

6. **Verify persistence after the call.** Fetch `t_cd34` again with `kanban_get`—do not trust only the completion response—and require:

   - status is `completed`/`done`/`closed` as expected;
   - persisted completion metadata contains `artifact_baseline`;
   - the persisted map is exactly equal to `BASELINE` (same paths and SHA-256 values, with no missing or substituted entries);
   - the recorded canonical verification command/result and completion evidence are present.

   Serialize the fetched card to a temporary card JSON in the shape expected by the external harness (exposing the persisted `artifact_baseline` at the card field the harness checks), then rerun the harness against the real target repository and the persisted card. Success is reported as two independent results:

   ```text
   Project verification: pass
   Ginflow harness: pass
   ```

If the completion call fails, the refetch is not completed, metadata is absent/different, or the persisted-card harness finds drift, report the operation as blocked—not safely complete. Do not replace the hash on the completed card. If drift appears after completion, stop and present the two Ginflow resolutions: restore the completed artifacts and create versioned docs plus a follow-up card, or reopen `t_cd34`, reconcile artifacts/implementation/acceptance/evidence, record a fresh baseline, rerun the harness, and complete again.
