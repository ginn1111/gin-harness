# Upstream migration baseline

Baseline captured before Hermes migration work.

| Item | Result |
| --- | --- |
| Upstream repository | `XiaoDuoYa/codex-with-chatgpt` |
| Upstream commit | `535a07dbb7aee887924c53767d985c09d405319d` |
| Node.js | `v22.23.0` |
| pnpm | `11.24.0` (repository-pinned via Corepack) |
| Git | `2.43.0` |
| OS | Ubuntu 24.04.5 LTS, Linux 7.0.0-31-generic, x86_64 |
| Hermes Agent | `v0.21.5+3903.g58d146e.dirty` (upstream `58d146e9`) |
| cloudflared | Not installed on baseline host; tunnel-specific E2E remains blocked until installed |
| `pnpm install` | Passed |
| `pnpm typecheck` | Passed (`tsc --noEmit`) |
| `pnpm build` | Passed (`tsc -p tsconfig.json`) |
| `pnpm test` | Passed: 18 files, 199 tests |

## Commands

```bash
corepack enable
pnpm install
pnpm typecheck
pnpm build
pnpm test
```

Untouched upstream completed install, typecheck, build, and test successfully. Missing `cloudflared` does not affect these baseline checks, but it must be installed before tunnel and live connector acceptance tests.
