No. The solo-dev drift gate should not block this unrelated work.

For completed card `APP-10`, the comparison is path-scoped: compare only the artifact paths recorded for the card against its completion commit `def456`. Here that scope is exactly:

- `docs/briefs/APP-10.md`

Do not compare the whole repository. A later change to `src/cache.py` is outside `APP-10`’s linked-artifact baseline, so it is not completed-card artifact drift. Because the linked brief has not changed, `APP-10` remains usable as authority and the unrelated work may continue.

The gate would block use of `APP-10` only if its recorded baseline were invalid or unavailable, its recorded path list no longer matched the card’s linked local docs, or `docs/briefs/APP-10.md` were missing, committed after `def456`, or changed in the working tree. Normal project verification and scope checks for the new work still apply separately.