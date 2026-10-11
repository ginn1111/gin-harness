---
status: completed
size: L
scope: core/ginflow-core provider-document builder, local provider, package/card/gate integration
owner: ginb
---
# Spec — PDOC-20 Local provider documents end to end

Refs: ginn1111/gin-harness#20 (slice of #18). Architecture: `docs/adrs/0001-artifact-first-execution-packages.md`, `GLOSSARY.md`.

## Objective

One consolidated local Markdown record per Work Unit is the canonical governance document. No separate stored Contract/Spec/Plan files for new work.

## Contract

- **L1 Builder.** New `core/ginflow-core/provider_document.py` exposes one public `build_provider_document(provider, work_package, target) -> dict` returning `provider`, `title`, `body`, `target_hints`, `metadata`, `content_hash`. Pure: no filesystem, network, or credentials. Unknown provider raises.
- **L2 Work Package.** Required: key, objective, scope, acceptance, contract, spec, plan, verification. `dependencies` and `risks` optional; empty optional sections render deterministically (omitted heading, never empty boilerplate). Incomplete package raises before render.
- **L3 Render.** Visible sections in fixed order: Objective, Scope, Acceptance, Contract, Spec, Plan, Verification, Dependencies, Risks. Local rendering puts machine metadata (provider, work unit key, schema) in YAML frontmatter at byte 0.
- **L4 Hash.** `content_hash` = sha256 of final rendering after newline and trailing-space normalization only. Order and all other content significant.
- **L5 Local adapter.** Outside the builder. Path `docs/work-units/<UNIT-KEY>.md` (assumption A1). Missing file: write. Existing file with equal metadata and hash: adopt. Existing file that differs: block, never overwrite.
- **L6 Package validation.** `validate_package` accepts one provider-neutral document reference `{provider, id, path_or_url}` per unit, rejects missing or mismatched references. Legacy v2 packages without references keep current behavior until #25.
- **L7 Cards.** `create_execution_cards` keeps cards blocked, concise (Objective, Scope, Acceptance, Verification, Dependencies, document link). Detailed Contract/Spec/Plan text is not copied. Structured reference lives in card metadata.
- **L8 Gate.** `ginflow-gate` review/completion requires `document_baseline` = `{content_hash, commit}` with committed content, hash equal to a recomputed hash of the committed file, and passing project verification evidence. Missing or drifted baseline rejects.

## Non-goals

GitHub/Linear providers (#22/#23), config resolution (#21), migration (#24), legacy removal (#25), tracker status sync.

## Assumptions to confirm

- A1: local path `docs/work-units/<UNIT-KEY>.md`.
- A2: gate recomputes the hash from the committed file via `git show <commit>:<path>`; no network.

## Verification

`make lint && make test`; new `core/ginflow-core/test_provider_document.py` (builder, hash, local adapter collisions); lifecycle test extended with a local-provider path.
