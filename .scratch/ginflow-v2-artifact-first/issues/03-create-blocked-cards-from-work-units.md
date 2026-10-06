# 03 — Create blocked cards from approved Work Units

**What to build:** Turn an approved package into one fully linked, blocked Kanban card per Work Unit plus one final Integration Card. Every card uses stable keys, points to the shared package artifacts and its own Plan, and carries enough native execution settings for later dispatch.

**Blocked by:** 02 — Shape and approve complete execution packages.

**Status:** ready-for-agent

- [ ] Every Work Unit creates exactly one blocked card with complete objective, scope, acceptance, verification, dependencies, and links.
- [ ] One blocked Integration Card is created and depends on all required implementation branches.
- [ ] Cards share one committed package baseline while retaining native Hermes task IDs.
- [ ] Card creation cannot dispatch implementation early.
