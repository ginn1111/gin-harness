# Migration map

Status meanings:

- **PRESERVE:** reusable as-is unless characterization tests expose a defect.
- **ADAPT:** retain design, change executor-facing behavior or text.
- **REWRITE:** existing component is fundamentally Codex-specific.
- **REMOVE:** omit from normal Hermes workflow.
- **DEFER:** keep compatibility behavior in V1; migrate separately.
- **INVESTIGATE:** decision requires implementation or live evidence.

| Subsystem | Status | Evidence and action |
| --- | --- | --- |
| `src/mcp/` | PRESERVE | Registers only ten read-only observation tools with scopes and `readOnlyHint`; no coding harness behavior. |
| `src/auth/` | PRESERVE / ADAPT text | OAuth, PKCE, token hashing/rotation, and workspace binding are executor-neutral. Change Codex-facing consent/pairing prose later. |
| `src/pairing/` | PRESERVE | Pairing manager is executor-neutral. |
| `src/workspace/` | PRESERVE | Canonical containment, sensitive-file policy, bounded reads/search, and git observation define security boundary. |
| `src/tunnel/` | PRESERVE | Cloudflare quick/named tunnel lifecycle is executor-neutral; keep C2C names. |
| `src/execution/` | PRESERVE / ADAPT writer | Record format already supports optional executor. New records should emit `hermes`; old records remain readable. |
| `src/bridge/` | PRESERVE | Assembles read-only MCP, auth, pairing, tunnel, runtime, and local admin API. |
| `src/process/` | PRESERVE | Starts/reuses C2C bridge; does not start Codex. |
| `src/session/` | PRESERVE / ADAPT comment | Checkpoint schema and conversation modes are executor-neutral. Replace Codex-only comments/terminology. |
| `src/config/paths.ts` | DEFER | Default state directory contains `codex-with-chatgpt`; rename could strand auth/session/tunnel state. Keep V1. |
| `src/config/endpoint.ts` | DEFER | Stored connector names are compatibility-sensitive. Preserve existing labels until explicit migration exists. |
| `src/config/sandbox-allow.ts` | REMOVE from Hermes path / DEFER legacy | Mutates Codex `config.toml`; Hermes does not share that sandbox model. Keep only as deprecated explicit compatibility command if useful. |
| `src/config/ui-prefs.ts` | PRESERVE | Machine preferences are executor-neutral. |
| `src/cli/` | ADAPT | Setup/doctor currently call Codex sandbox allowlisting and user text names Codex. Preserve C2C lifecycle commands. |
| `skill/SKILL.md` | REWRITE | Contains Codex Skill paths, `iab` APIs, Codex thread model, Computer Use rules, and sandbox setup. Replace with Hermes Skill plus progressive references. |
| `README.md` / `README.zh-CN.md` | ADAPT later | Full rebrand only after behavior works. Preserve protocol/security claims that remain verified. |
| `docs/architecture.md` | ADAPT later | Replace Codex executor and Computer Use descriptions with verified Hermes browser control. |
| `docs/protocol.md` | ADAPT later | Preserve wire states and formats; replace sender terminology. |
| `docs/security.md` | ADAPT later | Preserve threat model; replace executor/control-surface wording. |
| `docs/troubleshooting.md` | REWRITE later | Current repair paths target Codex browser, Skill, and sandbox config. |
| `package.json` | ADAPT later | Rename package metadata after runtime migration; keep `c2c` binary. |
| `src/version.ts` | ADAPT later | Change display product name; keep `SERVICE_NAME = c2c-bridge`. |
| `LICENSE` | PRESERVE | Keep upstream attribution. |
| Existing tests | PRESERVE | Security and bridge tests are reusable. Add characterization only for uncovered invariants. |
| Generated `dist/` | REBUILD | Never edit directly; regenerate from TypeScript source. |

## Sandbox decision

`src/config/sandbox-allow.ts::ensureSandboxAllowlist` exists solely to add C2C state directory to Codex's `[sandbox_workspace_write].writable_roots` in `$CODEX_HOME/config.toml` or `~/.codex/config.toml`.

Hermes file and terminal tools do not consume Codex config. Hermes supports `HERMES_HOME` as its own profile/config root, but no equivalent writable-root mutation is required for normal local execution. Therefore:

- Hermes Skill must not call `c2c sandbox-allow`.
- Hermes setup/doctor must not mutate Codex configuration.
- Existing command may remain temporarily for legacy Codex compatibility.
- Do not add a Hermes sandbox equivalent without a reproduced permission failure.

## Initial implementation order

1. Characterize reusable security/state behavior.
2. Rewrite Skill around Hermes paths and browser tools.
3. Remove sandbox allowlisting from Hermes setup/doctor path.
4. Prove browser control through Skill procedures.
5. Prove single and multiple iteration loops.
6. Prove checkpoint/HANDOFF recovery.
7. Port setup/update flows.
8. Rebrand docs and metadata.
