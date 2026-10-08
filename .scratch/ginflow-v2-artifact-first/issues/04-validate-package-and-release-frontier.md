# 04 — Validate package and release runnable frontier

**What to build:** Validate the complete approved package and release only its safely runnable frontier. Invalid artifacts, dependency graphs, links, ownership, workspace allocation, commits, or baseline evidence fail before dispatch; valid independent root cards unblock while descendants remain gated.

**Blocked by:** 03 — Create blocked cards from approved Work Units.

**Status:** ready-for-agent

- [ ] Validation rejects missing or unapproved artifacts, incomplete required fields, duplicate keys, broken links, cycles, dirty paths, and missing baseline evidence.
- [ ] Validation rejects simultaneously runnable cards that share a mutable workspace without isolation.
- [ ] Successful validation unblocks only independent root cards.
- [ ] Child cards remain gated until all parent cards are done.
