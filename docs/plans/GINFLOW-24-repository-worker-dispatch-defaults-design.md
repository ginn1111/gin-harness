---
status: completed
size: S
scope: ginflow repository worker dispatch defaults
owner: ginb
---

# Design — Repository worker dispatch defaults

## Decision

Ginflow will allow `.ginflow.yaml` to carry an optional `worker` block that
stores repository-local dispatch defaults used when creating governed Kanban
cards. `board` and `workspace` remain the only required fields; the worker
block is recommended for reproducible dispatch and never invalidates a minimal
config.

## Config schema

```yaml
version: 1
ginflow:
  board: <Kanban board slug>
  workspace: /absolute/path/to/project
  worker:
    profile: <worker Hermes profile>
    provider: <provider name>
    model: <model name>
```

- `profile` maps to `kanban_create.assignee`.
- `provider` and `model` are passed as explicit `kanban_create` overrides when
  present.
- All three fields are optional; an absent block means "use the current profile
  and let the worker profile's own defaults apply".

## Resolution

Keep the existing project-context resolution untouched. Board precedence
remains:

1. explicit runtime/API board override;
2. `HERMES_KANBAN_BOARD`;
3. `ginflow.board` in `.ginflow.yaml`;
4. Hermes's active board.

Worker dispatch resolution is independent and per field:

1. explicit per-card user override;
2. `ginflow.worker.<field>` in `.ginflow.yaml`;
3. runtime fallback — current Hermes profile for `profile`; provider/model
   left unset (omitted from `kanban_create`).

Invalid configured worker values (wrong type, empty string, unknown field)
raise `WorkerDefaultsError` so card creation fails closed. They do not break
read-only board/workspace routing: `context_error` ignores the worker block.

## Card-creation flow

1. Validate project context and resolve the board.
2. Read configured worker defaults (`configured_worker`).
3. If any of `profile`/`provider`/`model` is absent, show the resolved
   fallback and recommend completing the worker block.
4. If the user supplies values, validate them (profile against available
   Hermes profiles; provider/model as literal identifiers without credential
   inspection) and persist atomically via `persist_worker_defaults` before
   card creation.
5. Build `kanban_create` arguments explicitly: always pass `assignee`; pass
   `provider` only when resolved; pass `model` only when resolved.
6. Create the card only after persistence succeeds or the user explicitly
   skips setup. Skipping leaves the config unchanged and re-prompts at the
   next creation.

Explicit per-card overrides never rewrite repository defaults.

## Error handling

- Missing worker block: valid; prompt before card creation.
- Partial worker block: missing fields are treated as unconfigured; prompt for
  the complete block.
- Wrong type / empty / unknown worker field: block card creation; ask to
  repair `.ginflow.yaml`.
- Unknown profile: reject persistence; keep existing config unchanged.
- Persistence failure: no card creation; original file untouched.
- Invalid provider/model pairing: Hermes may reject card creation; report the
  exact error and retain the config for user correction. Never substitute
  another model.

## Files

- `skills/ginflow/lib/project_config.py` — `configured_worker`,
  `worker_error`, `resolve_worker_dispatch`, `persist_worker_defaults`,
  `WorkerDefaultsError`, `WORKER_FIELDS`.
- `skills/ginflow/SKILL.md` — worker dispatch guidance and config example.
- `skills/ginflow/references/project-context.md` — resolution and prompt
  behavior.
- `scripts/test-project-config.py` — precedence, validation, persistence.
- `skills/ginflow/scripts/test-kanban-harness.py` — argument mapping and
  fallback coverage.
- This design document.

## Acceptance

- Minimal configs (board + workspace only) remain valid.
- Configured defaults deterministically populate `kanban_create` arguments.
- Missing defaults prompt before each governed card creation; entered defaults
  persist atomically.
- Skipped setup uses current profile and omits provider/model.
- Malformed worker values block card creation without breaking read-only
  routing.
- No Hermes global config, CLI, or `.hermes/ginflow.yaml` behavior is added.
- `make lint` and `make test` pass.