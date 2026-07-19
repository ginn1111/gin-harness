## Gate decision

**Block any resume, handoff, or derived work that uses APP-9 as authority.** APP-9 is completed, and its path-scoped artifact baseline identifies completion commit `abc123` and the exact linked artifacts:

- `docs/briefs/APP-9.md`
- `docs/specs/APP-9.md`

The gate compares only those paths against `abc123`. Because a later commit materially changed `docs/specs/APP-9.md`, the completed-card linked-artifact baseline has drifted. Do not resume work from APP-9 or silently advance its completion commit. Unrelated cards and work outside these linked paths remain unblocked.

A human must choose and record a resolution:

1. **New intent:** Restore the completed APP-9 artifact state, create new versioned documentation for the changed intent, create a follow-up card, and link both the new docs and follow-up card back to APP-9.
2. **Changed completed scope:** Reopen APP-9; reconcile its brief/spec with the implementation, acceptance criteria, and verification evidence; commit the reconciled result; record the new completion commit and exact linked paths; rerun canonical project verification and the external Ginflow harness; then mark APP-9 completed again.
3. **Editorial only:** This is available only after explicit human classification that the change is non-material/editorial. Commit the editorial change, advance the baseline commit, and record an approval note without reopening implementation work. Because the stated spec change is material, this option does not apply unless a human explicitly overturns that classification.

Until one applicable resolution is completed, APP-9 cannot be used as the source of truth for resumed or derived project work.