# Install Hermes-native profiles and plug shared integrations

Run commands from setup repo root.

## 1. Install Hermes Agent

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
# or: pip install hermes-agent
hermes --version
hermes doctor
```

Authoritative docs: <https://hermes-agent.nousresearch.com/docs/user-guide/profiles>

## 2. Install profile distributions natively

Profile package and identity stay in their original distribution repositories, not this setup repo.

```bash
hermes profile install github.com/owner/profile --alias
hermes profile list
hermes profile info <profile>
```

Local distribution directory also works:

```bash
hermes profile install /absolute/path/to/profile-distribution
```

Distribution root must contain `distribution.yaml`. Hermes previews manifest before installation unless `--yes` is supplied.

## 3. Plug setup integrations

```bash
make doctor
make community-update                         # optional
make setup                                # preview default gintary profile
make setup PROFILES="profile-a"          # preview named profile
make apply PROFILES="profile-a"
make verify PROFILES="profile-a"
```

Setup requires existing profiles. It adds only:

- Ginflow skill
- setup-repo and optional community skill directories
- `ginflow-gate` plugin
- CodeGraph MCP and its toolset
- common CLI toolsets needed by harness/workflow

Setup preserves profile-owned `SOUL.md`, `distribution.yaml`, provider/model identity, secrets, memories, sessions, auth, cron, and release metadata.

Restart active sessions after apply.

## Update profiles

Use Hermes-native update against source recorded in profile manifest:

```bash
hermes profile update <profile>
```

Default update replaces distribution-owned `SOUL.md`, `skills/`, `cron/`, and `mcp.json`, while preserving local user data and `config.yaml` overrides. To intentionally accept distribution config changes:

```bash
hermes profile update <profile> --force-config
```

Profile update may replace integration links or config entries. Reapply kit:

```bash
make apply PROFILES="<profile>"
make verify PROFILES="<profile>"
```

## Package profiles using Hermes-native format

Do this in profile distribution repo or with Hermes export. Do not copy package data into setup repo.

### Git distribution

Profile distribution root includes at minimum:

```text
distribution.yaml
SOUL.md
config.yaml          # optional native defaults
skills/              # optional distribution-owned skills
cron/                # optional distribution-owned jobs
mcp.json             # optional distribution-owned MCPs
```

Keep secrets and runtime data out: `.env`, auth, memories, sessions, state DB, logs, caches.

Install directly from Git:

```bash
hermes profile install github.com/owner/profile
```

### Archive distribution

```bash
hermes profile export <profile> -o <profile>.tar.gz
hermes profile import <profile>.tar.gz
```

## Verify and test

```bash
make verify PROFILES="profile-a"
make verify-strict PROFILES="profile-a"
make test
```

Normal verification treats setup source edits as advisory. Strict mode fails on integration-source drift.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Profile missing | `hermes profile install <distribution> --name <profile>` |
| Profile lacks source metadata | Inspect `hermes profile info <profile>`; reinstall from proper distribution if needed |
| Ginflow missing | `make apply PROFILES="<profile>"` |
| CodeGraph connection fails | Install CodeGraph, then `hermes -p <profile> mcp test codegraph` |
| Tools not visible | Restart profile session after apply |
| Native profile update removed integrations | Re-run apply and verify |
| Need to change identity/package | Change original distribution repo, release it, then run `hermes profile update <profile>` |

## Target project

Do not implement product work in setup repo. Start target repo with local rules when needed:

```bash
cp /path/to/agents-hype/templates/AGENTS.md /path/to/project/AGENTS.md
```
