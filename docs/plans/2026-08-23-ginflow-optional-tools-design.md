# Ginflow Optional CodeGraph and MCP Workspace Checks

**Status: validated design**

## Goal

Extend the external Ginflow harness with non-blocking workspace-health checks for CodeGraph and configured Hermes MCP servers. Missing optional tooling must produce a concrete recommendation, not a completion blocker.

## Scope

- `skills/ginflow/scripts/validate-harness.py`
- `skills/ginflow/scripts/test-kanban-harness.py`
- CodeGraph state for the target workspace
- Hermes MCP configuration/connectivity for the inferred current profile

No target-project scanner or policy files are added.

## Profile inference

Resolve the current Hermes profile in this order:

1. Non-empty `HERMES_PROFILE`.
2. Active profile marker from `hermes profile list` (`◆` or `*`), using a bounded subprocess timeout.
3. No profile when inference fails; report MCP checks as skipped rather than guessing.

## CodeGraph checks

For the target workspace:

- Missing executable → warning and install recommendation.
- Missing `.codegraph/` or failed status → warning with `codegraph init <target>` recommendation.
- Stale index → warning with `codegraph sync <target>` recommendation.
- Healthy index → pass.
- Timeout or unexpected output → warning with `codegraph status <target>` recommendation.

Use real CLI commands only: `codegraph status`, `codegraph init`, and `codegraph sync`.

## MCP checks

For the inferred profile, read configured `mcp_servers` from its native config. Test each configured server with a bounded:

```text
hermes -p <profile> mcp test <server>
```

Report configured-and-connected servers as pass. Report missing configuration, failed connection, or timeout as non-blocking warnings with the exact remediation command. Never expose credentials or raw secret-bearing config values.

## Result contract

Add an `optional_tools` or `workspace` subsystem to the existing validator result. Each finding should include stable machine-readable fields:

- tool/server name
- state
- severity (`warning` or `pass`)
- evidence
- recommendation

Optional-tool warnings must not alter existing card, artifact, verification, scope, or lifecycle blocker decisions. Human output should include a concise `Workspace warnings`-compatible recommendation; JSON output must preserve the same facts without requiring text parsing.

## Error handling

All external commands use bounded timeouts. Non-zero exits, missing executables, absent profile config, missing index, and malformed status output become classified warnings. The validator must never hang or fail the harness solely because optional tooling is unavailable.

## Testing

Add deterministic tests using temporary workspaces, fake executables, and temporary Hermes config. Cover:

- `HERMES_PROFILE` precedence.
- Active profile marker fallback.
- No-profile fallback.
- CodeGraph missing, uninitialized, stale, healthy, malformed, and timeout states.
- MCP server absent, configured, connected, failed, and timeout states.
- Warning output in human and JSON modes.
- Valid harness remains non-blocking when optional tools are unavailable.

Run:

```bash
make test
make harness-test
make verify-test status-transition-test
```

`harness-test` requires an explicitly configured active profile when run locally, for example `HERMES_TEST_PROFILE=gintary`.
