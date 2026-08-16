---
status: completed
size: XS
owner: ginb
---

# Brief — GINFLOW-14 Ownership mapping on Gin-harness-flow

## Objective
Put implementation ownership mapping directly on the Gin-harness-flow page.

## Scope
- `docs/architecture/gin-harness-system.drawio`
- Gin-harness-flow page only; Harness system overview preserved unchanged.

## Acceptance criteria
- [x] Flow nodes show plugin/core/skill/shared ownership labels.
- [x] Coverage colors remain green verified, red expected but missing, yellow proposed.
- [x] Readable ownership and coverage legend appears on flow page.
- [x] Harness system overview page remains unchanged.
- [x] XML parse passes.
- [x] `make lint && make test` passes.

## Verification
- XML parse: passed.
- `make lint && make test`: passed.

**Status: completed**
