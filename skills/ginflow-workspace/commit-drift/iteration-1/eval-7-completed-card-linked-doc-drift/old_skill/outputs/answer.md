## Gate decision

**Block all target-project execution until APP-9's completed-card artifact drift is resolved.** Before startup, resume, handoff, or new execution involving a completed card, Ginflow requires a baseline containing the path and SHA-256 of every target-local linked artifact and compares the current files with those hashes.

APP-9 links:

- `docs/briefs/APP-9.md`
- `docs/specs/APP-9.md`

A completion commit such as `abc123` is not the required SHA-256 artifact baseline. Moreover, the later material change to `docs/specs/APP-9.md` would produce a hash mismatch against any valid completion-time baseline. Either condition is suspected post-completion drift. Do not resume from APP-9 and do not silently re-baseline it. Keep the blocker and proposed resolution on the card until a human chooses and completes one of these options:

1. **Treat the change as new intent:** Restore the completed APP-9 artifact, create new versioned documentation and a follow-up card for the changed intent, and link both back to APP-9.
2. **Treat the change as changed APP-9 scope:** Reopen APP-9, reconcile the linked artifacts with the implementation, acceptance criteria, and verification evidence, record fresh SHA-256 baselines for all linked target-local artifacts, rerun the Ginflow harness, and complete APP-9 again.

No work may resume from APP-9 until one of these resolutions has been completed and the gate passes.