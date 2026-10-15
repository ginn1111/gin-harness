---
status: completed
size: L
scope: skills/ginflow/lib/project_config.py documentation-provider config, adaptive resolution, migration preview/backup
owner: ginb
---
# Spec — PDOC-21 Configure and resolve document providers during setup

Refs: ginn1111/gin-harness#21 (slice of #18).

## Objective

Setup establishes one explicit documentation authority per project, validated and reversible.

## Contract

- **C1 Config block.** Optional strict `ginflow.documents` in `.ginflow.yaml` (assumption A1):
  `provider: adaptive|local|github|linear`, `github: {repo: owner/name}`, `linear: {team: <id>, project: <id optional>}`, `status_map: {start, block, resume, review_request, request_changes, complete}` (github/linear only). Unknown field, wrong type, unknown provider: error. Unrelated owned keys preserved on write.
- **C2 Adaptive.** Resolves to a concrete provider from exact directives, in order: portable agent instructions (`AGENTS.md`), Hermes-specific (`.hermes.md`), explicitly linked agent docs, existing canonical provider references. Directive syntax (assumption A2): a line `ginflow-docs: provider=<local|github|linear> [repo=owner/name | team=<id> project=<id>]`. Two sources at the same level that disagree, or any conflict: stop and ask. No evidence: stop and ask. Installed tools and credentials never select a provider.
- **C3 Report.** Resolution returns configured value, effective provider, evidence (file and line), destination, readiness.
- **C4 Targets.** GitHub repo `owner/name` or an unambiguous origin remote. Linear stable team/project IDs; human names are resolved to IDs by an injected resolver and the ID is persisted.
- **C5 Status map.** For github/linear every key above is required and non-empty; local has none. Agents never infer provider states.
- **C6 Migration.** Outdated or malformed config stays read-only. Migration: preview exact diff, require explicit approval, write timestamped backup under `.ginflow/migrations/` (ignored), then write atomically. No provider-document content in backups.
- **C7 Readiness.** Policy may be saved without credentials; governed creation fails closed with a readiness action (injected checker; no live calls in tests).

## Non-goals

Document building (#20), remote adapters (#22/#23), card migration (#24).

## Assumptions to confirm

- A1: config keys as listed. A2: directive syntax as listed.

## Verification

`make lint && make test`; extend `skills/ginflow/scripts/test-project-reviewer.py` pattern with a new `test-document-config.py` covering success, conflict, no-evidence, target validation, status map, preview/approve/backup, malformed, credential-less save.
