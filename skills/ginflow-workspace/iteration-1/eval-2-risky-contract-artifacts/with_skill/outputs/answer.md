# SEC-9 build-dispatch package

Status: **blocked before build dispatch**. Storage architecture remains unapproved. Architecture owner must decide proposed ADR before implementation starts. No code changes.

## Artifact paths

- `docs/briefs/SEC-9.md`
- `docs/specs/SEC-9.md`
- `docs/plans/SEC-9.md`
- `docs/adrs/0009-refresh-token-storage.md`
- `docs/cards/SEC-9.md`

## `docs/briefs/SEC-9.md`

```md
---
status: draft
size: L
scope: web and mobile authentication
owner: TBD — security/product owner
---

# Brief — SEC-9 rotating refresh tokens

## Objective
Replace session-cookie-only authentication with rotating refresh tokens for web and mobile clients while preserving active sessions during rollout and detecting token theft.

## Scope
- Web and mobile refresh-token issuance, rotation, revocation, and session continuity.
- Backward-compatible coexistence with existing session cookies during migration.
- Theft/replay detection, security audit events, staged rollout, and rollback.
- Authentication service/client contracts and required verification.

## Acceptance criteria
- [ ] Existing valid cookie sessions continue without forced logout throughout rollout.
- [ ] Updated web and mobile clients can obtain and rotate refresh tokens while supported legacy clients continue using valid cookies.
- [ ] Reuse of a superseded refresh token is detected, affected token family is revoked, and a security audit event is recorded.
- [ ] Rollout can stop or roll back to cookie authentication without invalidating sessions that were valid before rollout.
- [ ] Authentication issuance, rotation, replay detection, revocation, migration, and rollback actions produce queryable audit records without token secrets.
- [ ] `make verify` passes after implementation.

## Non-goals
- Redesign login, identity proofing, authorization, or account recovery.
- Select token storage architecture without architecture-owner approval.
- Remove legacy cookie support in this card.

## Dependencies and blocker
- Proposed storage ADR: `../adrs/0009-refresh-token-storage.md`.
- Build dispatch blocked until architecture owner accepts a storage strategy and unresolved contract values in spec are approved.
```

## `docs/specs/SEC-9.md`

```md
# Spec — SEC-9 rotating refresh-token contract

## Actors and invariants
- Actors: authentication service, web client, mobile client, existing cookie client, audit consumer, operator.
- Access-token behavior outside refresh exchange is unchanged unless separately approved.
- Refresh tokens must be opaque to clients, confidential in transit and at rest, and never written to logs or audit payloads.
- Each refresh token belongs to one server-recognized token family and is single-use after successful rotation.
- Existing valid cookie sessions must remain valid during rollout; migration must not force reauthentication.

## Behavior

### B1 — compatibility and migration
- Server must accept valid legacy session cookies and the new refresh-token flow concurrently behind independently controllable rollout gates.
- A valid cookie session may be upgraded to a refresh-token family without ending that cookie session.
- Web and mobile rollout percentages must be independently controllable.
- Legacy clients must continue to function while compatibility mode is enabled.
- Cookie retirement is out of scope and must require separate evidence and approval.

### B2 — issuance and rotation
- On eligible authenticated login or session upgrade, server must issue a refresh token using the storage strategy accepted in ADR 0009.
- On a valid refresh request, server must atomically invalidate the presented generation and issue exactly one successor in the same family.
- Concurrent use of one generation must yield at most one successful successor. Other uses must follow B3.
- Client transport and storage details for web and mobile are TBD in ADR/security review; implementation must not begin by assuming cookie, browser storage, keychain, or equivalent.

### B3 — theft/replay detection
- Presentation of a previously consumed, revoked, malformed, expired, or unknown refresh token must never issue credentials.
- Reuse of a consumed token must be treated as suspected theft: revoke its active family, deny refresh, and record a high-severity audit event.
- Family revocation must not revoke unrelated devices or the still-valid legacy cookie session unless an approved security policy explicitly requires that wider response.
- Response must not disclose whether a token existed, was consumed, or was revoked.

### B4 — failures and retries
- Rotation must be atomic. Storage or issuance failure must not leave both old and new generations usable.
- If request outcome is unknown because client loses response, retry behavior must not create two valid successors. Exact idempotency contract is TBD with storage decision.
- Unavailable token storage must fail closed for refresh issuance and rotation while legacy cookie authentication remains available during compatibility mode.
- Audit-delivery failure must be observable and retried or durably buffered; it must not leak token material. Whether security-sensitive rotation fails when audit durability is unavailable is TBD for security owner.

### B5 — rollback
- Operators must be able to disable new issuance and refresh exchange independently for web and mobile.
- Rollback must restore cookie-first behavior without deleting legacy sessions or requiring logout.
- Existing refresh-token records must be retained and protected during rollback until an approved retention/recovery decision permits revocation or deletion.
- Re-enabling rollout must not resurrect consumed or revoked tokens.

### B6 — audit and observability
- Audit events must cover issuance, successful rotation, denied refresh reason category, replay detection, family revocation, cookie-to-token migration, rollout-gate change, and rollback.
- Each event must include timestamp, actor/service, client class, account ID, session/device identifier where available, token-family identifier safe for logs, request/correlation ID, outcome, and reason category.
- Events must not contain raw refresh/access tokens, cookie values, token hashes usable as bearer substitutes, or unrelated personal data.
- Metrics/alerts must expose refresh success/error rates, replay detections, family revocations, migration counts, legacy-cookie usage, storage errors, and audit pipeline failures by client class and rollout cohort.
- Audit retention and access policy: TBD — security/compliance owner.

## API and security contract
- Exact endpoint, request/response schema, expiry, rotation grace policy, proof/binding, CSRF controls for web transport, secure mobile storage, rate limits, and error codes are TBD and require security/architecture approval.
- All refresh endpoints must require TLS, apply abuse controls, avoid secret-bearing telemetry, and return non-enumerating errors.
- Storage must support atomic single-use rotation, family lookup/revocation, expiry, audit correlation, and safe rollback. Accepted design must be recorded in ADR 0009.

## Behavioral acceptance
- [ ] A valid cookie-only web or mobile session remains usable before, during, and after enabling then rolling back token issuance.
- [ ] One valid refresh token produces one successor; presenting the old token again produces no credentials, revokes its family, and emits replay and revocation audit events.
- [ ] Two concurrent exchanges of one token produce at most one usable successor.
- [ ] Malformed, expired, unknown, and revoked tokens receive non-enumerating failures and no credentials.
- [ ] Storage failure issues no refresh credentials while a valid legacy cookie session remains usable in compatibility mode.
- [ ] Web and mobile rollout gates can be enabled and rolled back independently.
- [ ] Audit/log inspection confirms required fields and absence of token/cookie secrets.
- [ ] Re-enable after rollback does not make consumed or revoked generations valid.

## Open decisions blocking build
- Architecture owner: storage alternative and atomicity/idempotency mechanism.
- Security owner: client transport/storage, expiry/grace, theft-response blast radius, CSRF/binding, audit-failure policy, retention, and rate limits.
- Product/mobile/web owners: supported legacy-client window and rollout cohorts.
```

## `docs/adrs/0009-refresh-token-storage.md`

```md
# ADR 0009 — Refresh-token state storage

- Card: `../cards/SEC-9.md`
- Status: **proposed**
- Decision owner: TBD — architecture owner

## Context and drivers
SEC-9 requires atomic single-use rotation, token-family replay detection and revocation, web/mobile migration without forced logout, audit correlation, staged rollback, expiry, and high availability. No storage strategy has architecture approval.

## Viable alternatives

### A. Existing relational database
Store keyed token-family/generation state, preferably only verifier digests rather than bearer values; use transactions and uniqueness/locking for rotation.

- Benefits: durable state, transactional atomicity, established backup/audit operations, straightforward rollback retention.
- Costs: authentication traffic/load, cleanup work, schema migration, hot-row/concurrency risk.

### B. Dedicated strongly consistent key-value store
Use conditional writes/compare-and-swap plus TTL and durable configuration appropriate to security state.

- Benefits: low-latency token operations, native expiry, isolated auth workload.
- Costs: new operational dependency if not already approved, durability/restore and consistency validation, harder audit joins, rollback/recovery complexity.

### C. Hybrid relational families plus cache/denylist
Keep authoritative family state in relational storage; use cache for acceleration or short-lived replay markers.

- Benefits: durable authority with scalable reads/detection.
- Costs: two-store consistency and invalidation failure modes, more complex rollback, cache must never become ambiguous authority.

### D. Stateless signed refresh tokens plus revocation/reuse store
Encode claims in signed tokens while retaining server-side family/replay state.

- Benefits: reduced lookup data for validation.
- Costs: still needs authoritative state for required theft detection and revocation, key-rotation complexity, claim/privacy exposure, larger attack surface; does not remove core storage decision.

## Proposed decision
TBD. Architecture owner must select and document one alternative, atomic rotation mechanism, hashing/key handling, consistency/durability requirements, backup/restore behavior, retention/cleanup, capacity limits, and rollback treatment.

## Consequences
No implementation or build dispatch until status becomes `accepted`. Proof must demonstrate atomic concurrent rotation, replay-family revocation, outage behavior, audit correlation, and rollback recovery for selected store.
```

## `docs/plans/SEC-9.md`

```md
# Plan — SEC-9 rotating refresh tokens

1. **Resolve architecture and security contracts.** Architecture/security owners review `docs/adrs/0009-refresh-token-storage.md` and spec open decisions; record accepted storage, transport, atomicity/idempotency, expiry, theft response, retention, and audit-failure policy. Evidence: accepted ADR plus no material `TBD` blocking behavior. Covers B2–B6. **Stop if not approved.**
2. **Map current auth paths and compatibility boundaries.** Identify cookie issuance/validation, web/mobile auth clients, session persistence, audit pipeline, feature gates, and relevant tests/paths. Evidence: card update with confirmed components and legacy-client matrix. Covers B1, B5.
3. **Add contract tests before behavior changes.** Add focused tests for cookie continuity, single-use/concurrent rotation, replay-family revocation, non-enumerating failures, storage/audit failure, independent client gates, rollback, and secret-free audit records. Evidence: tests fail for missing new behavior while existing baseline remains understood. Covers all behavioral acceptance.
4. **Implement accepted server-side token state and audit contract.** Change only confirmed auth/storage/audit components; include expiry and cleanup required by accepted ADR. Evidence: focused service/storage tests pass. Covers B2–B6.
5. **Implement backward-compatible web and mobile adoption.** Add independently gated client flows while retaining legacy cookies and secure transport/storage approved by security review. Evidence: integration tests prove updated and legacy clients coexist without logout. Covers B1–B4.
6. **Exercise staged migration and rollback.** Test disabled, partial web, partial mobile, full eligible rollout, rollback, and re-enable states; inject concurrency and storage/audit failures. Evidence: runbook/test results show cookie continuity and no resurrection of consumed/revoked tokens. Covers B1, B3–B6.
7. **Run canonical verification and dispatch evidence review.** Run `make verify` from worktree root. Evidence recorded verbatim on card: command, timestamp, exit status, and summary; review changed files against SEC-9 scope and confirm no token secrets in logs/fixtures. Dispatch complete only with fresh passing result.
```

## `docs/cards/SEC-9.md`

```md
# SEC-9 — Replace session cookies with rotating refresh tokens

- Status: blocked
- Assignee: unassigned
- Workspace: `worktree`
- Objective: Introduce rotating refresh tokens across web and mobile without forced logout, with theft detection, rollback, and audit logging.
- Scope: auth service plus web/mobile auth integration; retain legacy cookie compatibility. Excludes cookie retirement and unrelated login/authorization redesign.
- Acceptance: session continuity; compatible migration; atomic rotation; replay detection and family revocation; safe rollback; secret-free audit trail; fresh passing `make verify`.
- Brief: `../briefs/SEC-9.md`
- Spec: `../specs/SEC-9.md`
- Plan: `../plans/SEC-9.md`
- Proposed ADR: `../adrs/0009-refresh-token-storage.md`
- Blocker: architecture owner has not accepted storage strategy; security contract TBDs remain. Do not dispatch build.
- Next step: architecture and security owners review ADR/spec, record decisions, then move card to build-ready.
- Verification: not run — shaping only; no implementation. Canonical command for build: `make verify`.
```

## Dispatch gate

Dispatch only when ADR status is `accepted`, named owners resolve material spec `TBD`s, brief/spec/plan remain aligned, card has assignee, and worktree points at real target repo. Implementation completion requires fresh `make verify` evidence on card.
