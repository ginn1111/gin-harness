# Codex coupling inventory

## Classification

- **A — documentation only**
- **B — branding only**
- **C — Skill/instruction coupling**
- **D — runtime coupling**
- **E — test coupling**
- **F — compatibility concern**

Search scope excluded generated `dist/`, `.git/`, and `node_modules/`. Generated `dist/` mirrors source and must be rebuilt after source changes.

| File | Class | Coupling | Action |
| --- | --- | --- | --- |
| `skill/SKILL.md` | B/C/D | Primary Codex workflow: `CODEX_HOME`, `~/.codex/skills`, `iab`, Computer Use prohibition, Codex thread semantics, sandbox allowlisting, INIT/PLAN/EXECUTED/HANDOFF loop | REWRITE for Hermes; preserve C2C protocol/checkpoints |
| `README.md` | A/B/C/F | Product/install/usage text, Codex Skill path, Computer Use flow, sandbox command | ADAPT after behavior works |
| `README.zh-CN.md` | A/B/C/F | Chinese mirror of Codex install, browser, sandbox, architecture | ADAPT after behavior works |
| `docs/architecture.md` | A/B | Codex harness and Computer Use control-plane names | ADAPT later |
| `docs/protocol.md` | A/F | Codex named sender/executor throughout otherwise executor-neutral wire protocol | ADAPT terminology; preserve format |
| `docs/security.md` | A/D/F | Codex nominates logs; Computer Use pairing; legacy state path | ADAPT text; preserve controls/path compatibility |
| `docs/troubleshooting.md` | A/C/F | Codex Web GPT, Skill repair, browser actions, `CODEX_HOME`, sandbox config | REWRITE for Hermes; retain explicit legacy section only if supported |
| `docs/migration/baseline.md` | A/F | Upstream repository provenance | PRESERVE |
| `package.json` | B/F | Package name/description | ADAPT during product docs phase; preserve `c2c` binary |
| `LICENSE` | B/F | Upstream contributor attribution | PRESERVE |
| `src/version.ts` | B/D | `PRODUCT_NAME = "Codex with ChatGPT"` used in CLI/OAuth/MCP | ADAPT display name later; preserve service name |
| `src/config/paths.ts` | D/F | OS state directory named `codex-with-chatgpt` | DEFER rename; preserve V1 state compatibility |
| `src/config/endpoint.ts` | B/D/F | Default/stored connector name `Codex with ChatGPT` | DEFER migration; preserve existing connectors |
| `src/config/sandbox-allow.ts` | D/F | Directly reads/writes `$CODEX_HOME/config.toml` or `~/.codex/config.toml` and Codex writable roots | REMOVE from Hermes workflow; preserve optional legacy command |
| `src/cli/index.ts` | B/C/D/F | Codex description/help, setup/doctor sandbox mutation, Skill guidance, executor example | ADAPT |
| `src/auth/oauth.ts` | B/D | OAuth page and scope labels name Codex | ADAPT user-facing text only |
| `src/session/state.ts` | D/F | Codex-thread wording in comment; schema is neutral | ADAPT comment, preserve schema |
| `src/execution/records.ts` | D/F | Missing executor historically comes from Codex-era records | PRESERVE parser; new writes use `hermes` |
| `tests/sandbox-allow.test.ts` | E/F | Characterizes Codex TOML mutation | PRESERVE while legacy command exists; add Hermes setup assertions |
| `tests/cli-workspace-flag.test.ts` | E/F | Isolates `CODEX_HOME` for sandbox command | Keep only for legacy command compatibility |
| `tests/endpoint.test.ts` | B/E/F | Pins legacy connector names | PRESERVE compatibility expectations |
| `tests/session.test.ts` | E/F | Uses Codex connector fixture while testing neutral session state | PRESERVE fixture as legacy compatibility |
| `tests/helpers.ts` | B/E | Fixture text mentions Codex; generic sandbox comment | ADAPT fixture branding later; keep temp-dir strategy |
| `tests/mcp-integration.test.ts` | B/E | Asserts fixture text from helper | ADAPT with helper; no runtime Codex coupling |

## Hard runtime coupling

### Codex Skill and browser API

`skill/SKILL.md` is both orchestration logic and installation guide. It assumes:

- Codex Skill discovery and installation paths;
- Codex built-in `iab` browser object and thread lifetime;
- Codex Computer Use constraints;
- Codex writable-root sandbox behavior;
- Codex as executor named in every control message.

This is main rewrite seam. Bridge runtime does not implement coding harness.

### Codex sandbox configuration

`src/config/sandbox-allow.ts`:

- resolves `CODEX_HOME` or `~/.codex`;
- opens `config.toml`;
- modifies `[sandbox_workspace_write].writable_roots`;
- adds C2C state directory idempotently;
- preserves unrelated TOML content.

`src/cli/index.ts` invokes this during setup/doctor and exposes `sandbox-allow`.

Hermes has its own `$HERMES_HOME` config/profile location, but local file/terminal execution does not rely on Codex `sandbox_workspace_write`. No Hermes equivalent should be invented. Remove this call from Hermes workflow; retain old command only for explicit legacy compatibility.

## Compatibility-sensitive coupling

### Connector names

`src/config/endpoint.ts` preserves stored connector labels. Existing ChatGPT connectors may still be named `Codex with ChatGPT` or `Codex with ChatGPT · <workspace>`. Renaming without migration can break connector lookup and repair.

Decision: keep stored labels in V1. Introduce Hermes name only with explicit old/new discovery logic.

### State directories

`src/config/paths.ts` uses `codex-with-chatgpt` in OS state paths. Those directories contain auth hashes, tunnel state, endpoint state, sessions, runtime metadata, and execution records.

Decision: keep V1 path. A later rename needs fallback discovery and safe migration.

### Execution records

`src/execution/records.ts` permits absent executor for historical records. Absence remains unknown rather than force-labeled.

Decision: keep parser compatibility. New Hermes records set `executor="hermes"`.

### C2C protocol names

`docs/protocol.md` names Codex as sender, but `STATE`, `TASK_ID`, `ITERATION`, checkpoint names, and message sections are executor-neutral.

Decision: change documentation sender to Hermes. Do not rename protocol or state paths in V1.

## Low/no Codex coupling

| Area | Finding |
| --- | --- |
| `src/mcp/*` | No executor dependency beyond display product name imported from `src/version.ts` |
| `src/auth/*` | Protocol-neutral; only visible prose names Codex |
| `src/pairing/*` | Executor-neutral |
| `src/workspace/*` | Executor-neutral security/read layer |
| `src/tunnel/*` | C2C-branded, not Codex-dependent |
| `src/execution/output.ts` / `sanitize.ts` | Executor-neutral record/sanitizer behavior |
| `src/bridge/*` | Assembles C2C services; no Codex process |
| `src/process/*` | Manages C2C bridge process only |

## Search-term conclusions

- `CODEX_HOME` and `.codex`: real runtime coupling only in sandbox config and its tests/docs/Skill.
- `sandbox`: mix of Codex config coupling and generic sandbox/testing language; classify per file, not by term alone.
- `iab`: concentrated in Codex Skill browser procedures; rewrite.
- `Computer Use`: documentation/Skill description of Codex control plane; replace with verified Hermes browser tools.
- `skill` / `SKILL.md`: many generic references, but installation paths and browser APIs are Codex-specific.
