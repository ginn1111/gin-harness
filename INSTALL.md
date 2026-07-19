# Install and update managed Hermes profiles

This guide installs `gintary` and `ginb` from this checkout. Run commands from repo root.

## Prerequisites

Required:

- Hermes CLI
- Git
- Python 3
- PyYAML

CodeGraph is optional but configured for both profiles.

```bash
make doctor
make doctor-deps   # only when PyYAML is missing
```

## Install

1. Create machine-local provider config.

   ```bash
   cp .env.example .env
   ```

   Set `GIN_API_KEY`. Defaults already cover:

   ```dotenv
   GIN_BASE_URL=https://agents.gin1111.dev/v1
   GIN_HOST=agents.gin1111.dev
   ```

2. Install community skills.

   ```bash
   make community-update
   ```

   Script clones `https://github.com/mattpocock/skills.git` into `community/mattpocock-skills` or fast-forwards existing clone. Clone is made read-only.

3. Preview setup.

   ```bash
   make setup
   ```

   Preview still validates dependencies, parses profile registry, and blocks divergent profile-local skills before printing planned writes.

4. Apply setup.

   ```bash
   make apply
   ```

   Setup manages account-wide profile registry even when invoked inside profile-scoped Hermes session. It:

   - creates missing profiles with `--no-skills`
   - links canonical `SOUL.md`
   - links canonical `skills/ginflow`
   - renders `config.yaml` from `config/profile.yaml.tmpl`
   - backs up replaced regular files with timestamp suffix

5. Install profile secrets and opt out of bundled skills.

   ```bash
   for profile in gintary ginb; do
     cp .env "$HOME/.hermes/profiles/$profile/.env"
     hermes -p "$profile" skills opt-out
   done
   ```

   Use supported `skills opt-out` command. Do not create `.no-bundled-skills` manually.

6. Verify installation.

   ```bash
   make verify
   ```

## Verify

Normal verification separates deployed-profile failures from source edits:

```bash
make verify
```

It fails when profile installation, config, skills, workflow contracts, or configured MCP connection are broken. Dirty canonical source files produce non-fatal recommendation.

Strict verification also fails on tracked or untracked canonical source drift:

```bash
make verify-strict
```

Use strict mode for CI, release, or before declaring checkout synchronized with deployment.

## Update

Update repo-managed profile behavior and shared skills:

```bash
git pull
make community-update
make apply
make verify
make test
```

Update Hermes binary separately:

```bash
hermes update
make verify
```

Restart active Hermes sessions after config, skill, or MCP changes.

## Local maintenance

Remove generated Python caches and CodeGraph index:

```bash
make clean
```

Run deterministic source checks:

```bash
make test
```

`make harness-test` adds model-backed blank-project integration and may take longer. `make verify-test` expects canonical source drift and only tests normal/strict drift exit behavior.

## Start target project

Do not implement product work in this setup repo. Open target repo and add local rules when missing:

```bash
cp /path/to/agents-hype/templates/AGENTS.md /path/to/project/AGENTS.md
```

Edit copied file with real verification command, boundaries, generated-file authorities, and deployment constraints. Ginflow and selected Kanban card provide shared workflow and durable handoff.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Profile missing | Setup not applied against account registry | `make apply` |
| Profile appears missing only inside profile session | Stale `HOME` or `HERMES_HOME` scope | Use repo scripts; they normalize account home and clear `HERMES_HOME` |
| Setup blocks on profile-local skill drift | Local skill shadows canonical repo skill | Remove divergent copy or replace it with canonical symlink, then rerun `make setup` |
| No enabled skills | Community clone missing, config stale, or external path unavailable | `make community-update && make apply`, then `hermes -p <name> skills list` |
| Canonical `ginflow` link missing | Setup predates local worker link | `make apply` |
| `.no-bundled-skills` missing | Bundled-skill opt-out not applied | `hermes -p <name> skills opt-out` |
| Authentication fails | Missing or wrong `GIN_API_KEY` in profile `.env` | Fix repo `.env`, copy it to both profile directories, restart session |
| CodeGraph absent | Optional CLI not installed | Install from <https://github.com/colbymchenry/codegraph>, rerun `make apply`, then verify |
| CodeGraph configured but connection fails | CLI or MCP startup broken | Run `hermes -p <name> mcp test codegraph`; fix command before verification |
| Normal verify reports source drift | Canonical files changed locally | Review diff; use `make verify-strict` when drift must fail |

## Machine-local files

Never commit:

- `.env`
- `community/` clones
- `.codegraph/`
- profile `.env` files
- Hermes session/history/auth state
- Python caches
