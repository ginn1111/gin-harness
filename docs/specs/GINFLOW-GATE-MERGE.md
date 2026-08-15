# Merge ginflow-gate routing into ginflow-gate

## Problem Statement

Installing both `ginflow-gate` and `ginflow-gate routing` complicates setup and creates risk of duplicate or inconsistent plugin wiring. Users need one installable plugin while retaining separate routing and completion-gate responsibilities.

## Solution

Merge `ginflow-gate routing` into public plugin `ginflow-gate`. Keep routing and gate logic in separate internal modules, and have `ginflow-gate.register(ctx)` register all required hooks. Install only `ginflow-gate`.

## User Stories

1. As a Hermes administrator, I want to install one Ginflow plugin, so that setup is simpler.
2. As a profile maintainer, I want one public plugin name, so that plugin configuration is easier to understand.
3. As a Ginflow user, I want Kanban routing context injected before LLM calls, so that work starts in the correct workspace and card state.
4. As a Ginflow user, I want invalid Kanban completion blocked, so that lifecycle metadata remains trustworthy.
5. As a Ginflow user, I want linked artifacts marked completed after valid completion, so that documentation state stays synchronized.
6. As a maintainer, I want routing and gate logic separated internally, so that each responsibility remains testable and understandable.
7. As a maintainer, I want registration tested through the public plugin entry point, so that installation cannot silently omit a hook.
8. As a maintainer, I want stale standalone routing references removed, so that future setup does not install duplicate behavior.

## Implementation Decisions

- Public plugin identity remains `ginflow-gate`.
- Move routing behavior into the `ginflow-gate` plugin package while preserving separate routing and gate modules.
- `register(ctx)` explicitly wires `pre_llm_call` routing, `pre_tool_call` completion validation, and `post_tool_call` artifact updates.
- Routing errors are non-blocking no-op failures because routing supplies context rather than enforcing completion integrity.
- Completion validation remains fail-closed. Successful post-completion artifact updates may report warnings without undoing a successful completion.
- Remove standalone `ginflow-gate routing` source and managed installation references.
- No migration or backward-compatibility handling is included; users manage existing profiles manually.
- Move canonical plugin tests into the plugin package.
- Rename the Make target to `plugin-test` and make `make test` invoke it.
- Update setup/configuration documentation and the architecture diagram to show one plugin with separate routing and gate responsibilities.

## Testing Decisions

- Test through the highest existing seam: the public plugin registration and hook behavior.
- Verify all three hooks register from `ginflow-gate.register(ctx)`.
- Preserve real routing scenarios covering workspace filtering, explicit task selection, status mapping, blocked/terminal states, and linked-document validation.
- Preserve completion-gate scenarios covering required card fields, verification metadata, artifact baseline matching, drift rejection, and linked-artifact completion updates.
- Verify installation and source cleanup contain no stale `ginflow-gate routing` references.
- Canonical verification: `make lint && make test`.

## Out of Scope

- Automatic migration of existing profile configuration.
- Backward-compatible `ginflow-gate routing` shim.
- Changes to Ginflow routing or gate policy semantics beyond plugin relocation and registration.
- Production deployment or remote Git push.

## Further Notes

The architecture diagram should show one installable `ginflow-gate` container with separate routing and gate nodes, plus explicit `register(ctx)` wiring to both responsibilities.

Status: ready for agent.
Label: `ready-for-agent`
