# SEC-9 shaping result

**Status:** Blocked before build dispatch. L/risky work requires brief, spec, and plan. Refresh-token storage is material security architecture; no architecture-owner approval exists. Record and approve storage ADR before implementation card becomes ready.

## Required target-repo artifacts

### `briefs/SEC-9.md`

```markdown
---
status: blocked
size: L
scope: authentication across web, mobile, API, migration, observability, rollback
owner: unassigned
---

# Brief — Replace session cookies with rotating refresh tokens

## Objective
Replace session-cookie authentication across web and mobile with rotating refresh tokens while preserving active sessions during rollout, detecting refresh-token theft, supporting rollback, and producing auditable security events.

## Scope
- Web client, mobile clients, auth API, token lifecycle, migration compatibility.
- Refresh issuance, rotation, revocation, reuse detection, audit logging, rollout controls, and rollback.
- Existing session-cookie validation retained during compatibility window.

## Acceptance criteria
- [ ] Existing valid cookie sessions continue without forced logout throughout rollout.
- [ ] Web and mobile can exchange an existing authenticated session for the new token flow.
- [ ] Every successful refresh rotates the token and invalidates its predecessor atomically.
- [ ] Reuse of a rotated/revoked refresh token is detected and revokes the affected token family.
- [ ] Issuance, rotation, reuse detection, revocation, migration, and rollback events are audit logged without raw token material.
- [ ] Feature flags permit staged enablement by client/platform and immediate fallback to cookie validation.
- [ ] Rollback does not invalidate still-valid legacy sessions or strand migrated clients.
- [ ] `make verify` passes with migration, concurrency, theft-detection, compatibility, and rollback coverage.
- [ ] Architecture owner approves `adrs/SEC-9-refresh-token-storage.md` before dispatch.

## Non-goals
- Redesigning unrelated authorization or identity-provider flows.
- Removing legacy session-cookie support before migration exit criteria are met.
- Choosing token storage without architecture/security approval.

## Notes
Workspace: `worktree`.
Canonical verification: `make verify`.
```

### `specs/SEC-9.md`

```markdown
# Spec — Rotating refresh-token migration

## Problem
Session cookies cannot directly satisfy required cross-platform rotating-token behavior. Migration must avoid forced logout and must not weaken theft response, rollback, or auditability.

## Desired behavior
1. During compatibility phase, server accepts valid legacy session cookies and approved refresh-token credentials.
2. Authenticated legacy clients receive a migration path that creates a token family without invalidating their current session.
3. Each refresh is single-use: server atomically consumes current token, issues successor, and records lineage.
4. Concurrent use has one winner. Any later use of consumed token triggers reuse handling rather than another successor.
5. Reuse detection revokes token family, denies refresh, records security event, and requires normal reauthentication for that affected family only.
6. Rollout is gated separately for issuance and acceptance, by client/platform/version. Acceptance remains enabled until rollback and compatibility windows close.
7. Rollback stops new issuance and routes clients through retained compatible authentication; it does not mass-revoke valid legacy sessions.
8. Audit records contain actor/account ID, token-family ID or irreversible identifier, client/platform, event type, timestamp, request/correlation ID, outcome, and reason. Never log raw access or refresh tokens.

## Inputs / outputs
- Inputs: valid legacy session or refresh credential, client/platform/version, device/session context, request metadata.
- Success: short-lived access credential plus rotated refresh credential according to approved client-storage contract.
- Failure: stable auth error category; no credential leakage; security event when reuse or revocation applies.

## Constraints
- Storage, hashing/encryption, transaction boundaries, client secure-storage rules, token lifetime, and family schema require approved ADR.
- Rotation and predecessor invalidation must be atomic under retries and concurrent requests.
- Refresh credentials must not appear in URLs, analytics, application logs, or audit payloads.
- Legacy cookie support remains available through defined migration and rollback windows.
- Protocol changes remain backward compatible with released web and mobile versions.

## Acceptance criteria
- [ ] Migration tests prove active legacy sessions remain usable and can migrate without logout.
- [ ] Rotation tests prove predecessor cannot produce a second valid successor.
- [ ] Concurrency/retry tests prove deterministic one-winner behavior.
- [ ] Reuse tests prove family revocation and sanitized audit event emission.
- [ ] Mixed-version tests cover legacy-only, migration-capable, token-enabled, and rolled-back clients.
- [ ] Rollback test proves issuance can stop while valid legacy sessions keep working.
- [ ] Audit tests prove required fields and absence of raw secrets.
- [ ] `make verify` passes.

## Edge cases
- Two refreshes race from same web/mobile account or device.
- Response is lost after server commits rotation; retry uses predecessor.
- Mobile app stays offline across multiple rollout phases.
- User has several independent devices/token families; theft response limits blast radius to affected family unless policy says otherwise.
- Clock skew, expired credentials, revoked account, password reset, and explicit logout.
- Rollback occurs after some clients migrated but before all clients support new flow.
- Audit sink is slow or unavailable; auth path follows approved fail-open/fail-closed policy without losing required evidence.
```

### `adrs/SEC-9-refresh-token-storage.md`

```markdown
# ADR — SEC-9 refresh-token storage

Status: Proposed; architecture-owner approval required.

Decision required before dispatch:
- Server-side representation: opaque-token hash, encrypted token, or other approved design.
- Token-family lineage and atomic consume/rotate transaction model.
- Web storage and transport protections; CSRF/XSS implications.
- iOS/Android secure-storage and backup/migration behavior.
- Lifetimes, revocation retention, audit retention, key rotation, and deletion policy.
- Lost-response/retry policy and acceptable theft-detection false-positive behavior.
- Audit-sink failure policy.

Required reviewers: architecture owner and security owner.

Build remains blocked until decision, threat analysis, rollback effect, and approval are recorded.
```

### `plans/SEC-9.md`

```markdown
# Plan — SEC-9 rotating refresh tokens

1. Obtain architecture/security approval for `adrs/SEC-9-refresh-token-storage.md`; stop if unresolved.
2. Inspect auth boundaries, web/mobile credential handling, schema/migrations, feature-flag system, audit pipeline, and current `make verify` baseline.
3. Add contract tests first for legacy compatibility, no-forced-logout migration, atomic rotation, retries/races, reuse detection, audit redaction, mixed client versions, and rollback.
4. Add approved token-family persistence and atomic lifecycle operations behind disabled flags.
5. Add server acceptance/issuance paths while preserving legacy cookie validation.
6. Add web and mobile migration/storage flows using approved platform contracts.
7. Add sanitized audit events, metrics, alerts, and theft-response runbook.
8. Stage rollout: server acceptance, internal clients, small cohorts per platform/version, broader issuance; monitor migration success, refresh errors, reuse signals, and logout rate.
9. Exercise rollback: stop issuance, retain acceptance/legacy validation, verify migrated and legacy clients remain recoverable.
10. Remove legacy flow only under a separate approved task after compatibility window and exit metrics.
11. Run `make verify`; record exact result and `git status --short` on SEC-9 card.
```

### Kanban card `SEC-9`

```text
Title: Replace session cookies with rotating refresh tokens

Objective:
- Roll out rotating refresh tokens across web and mobile without forced logout, with theft detection, rollback, and sanitized audit logging.

Scope:
- Auth API, web/mobile auth clients, token persistence, migration compatibility, feature flags, audit/monitoring, tests.
- Do not remove legacy cookie validation or alter unrelated authorization flows.

Acceptance:
- Satisfy `briefs/SEC-9.md` and `specs/SEC-9.md`.
- Approved `adrs/SEC-9-refresh-token-storage.md` exists.
- `make verify` passes; exact fresh output recorded.

Workspace:
- worktree

Artifact links:
- `briefs/SEC-9.md`
- `specs/SEC-9.md`
- `plans/SEC-9.md`
- `adrs/SEC-9-refresh-token-storage.md`

Blocker:
- Storage strategy lacks architecture-owner approval. Do not dispatch build.

Next step:
- Architecture and security owners decide and approve ADR; then mark brief/card ready and dispatch one worker in `worktree`.
```

## Dispatch decision

Do not dispatch. Material storage, atomicity, client-storage, and retry semantics remain undecided. After ADR approval, retain all four artifact links on card, remove blocker, and dispatch with `worktree`; completion evidence must be fresh `make verify` output plus scoped `git status --short`.
