# Migration Mapping Approval

## Discovered profiles

- `<old-profile-1>`: `<routing/personality summary>`

## Proposed mapping

| New role | Source | Decision |
|---|---|---|
| ginb — builder | NEW / existing / SKIP | PENDING |
| ginr — reviewer | NEW / existing / SKIP | PENDING |
| gins — shipper | NEW / existing / SKIP | PENDING |
| gino — orchestrator | NEW / existing / SKIP | PENDING |

## Migration rules

- Targets are created with bundled skills disabled.
- Old skills, toolsets, memory, sessions, credentials, and environment configuration are not copied.
- Personality is selectively preserved and adapted.
- Shared and role-specific skills are added after personality review.
- Toolsets are rebuilt afterward using least privilege.
