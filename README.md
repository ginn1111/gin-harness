# agents-hype

Source repo for two managed Hermes profiles and their shared Ginflow workflow.

This repo installs and verifies global profile behavior. It is not a day-to-day project workspace. Product code, tests, local rules, and task artifacts belong in target project repos.

## Managed profiles

| Profile | Role | Source |
|---|---|---|
| `gintary` | Planner, dispatcher, escalation sink | `profiles/gintary.SOUL.md` |
| `ginb` | Builder, verifier, shipper | `profiles/ginb.SOUL.md` |

Both profiles route target-project work through the canonical [`ginflow`](skills/ginflow/SKILL.md) skill.

## Repository map

| Path | Purpose |
|---|---|
| `profiles/*.SOUL.md` | Canonical profile contracts |
| `config/profiles.yaml` | Managed profile names, descriptions, and display skins |
| `config/profile.yaml.tmpl` | Generated profile config template |
| `scripts/setup.sh` | Preview or apply profile installation |
| `scripts/verify.sh` | Verify deployed profiles and workflow contracts |
| `scripts/community-setup.sh` | Clone or fast-forward community skills |
| `scripts/detect-skill-drift.py` | Block profile-local copies that shadow canonical skills |
| `skills/ginflow/` | Live shared workflow skill, templates, harness, and tests |
| `skills/ginflow-workspace/` | Archived evaluation evidence; not loaded for live work |
| `templates/AGENTS.md` | Starter local rules for target repos |

Community skills are machine-local clones under `community/` and are not committed.

## Quick start

```bash
# 1. Install Hermes Agent if missing
pip install hermes-agent    # or download from github.com/nousresearch/hermes-agent/releases
hermes --version

# 2. Setup managed profiles
make doctor
cp .env.example .env
# Set GIN_API_KEY. Override GIN_BASE_URL or GIN_HOST only when needed.
make community-update
make setup       # preview
make apply       # writes deployed profile files

for profile in gintary ginb; do
  cp .env "$HOME/.hermes/profiles/$profile/.env"
  hermes -p "$profile" skills opt-out
done

make verify
```

`setup.sh` resolves real account home, clears profile-scoped `HERMES_HOME`, creates missing profiles, links each `SOUL.md`, links `ginflow` into each profile, and renders `config.yaml`. Existing regular `SOUL.md`, `config.yaml`, or local `ginflow` files are backed up before replacement.

`GIN_BASE_URL` defaults to `https://agents.gin1111.dev/v1`; `GIN_HOST` defaults to `agents.gin1111.dev`. Missing `GIN_API_KEY` does not block setup, but model authentication will fail until profile `.env` files contain it.

See [INSTALL.md](INSTALL.md) for update and troubleshooting commands.

## Commands

| Command | Action |
|---|---|
| `make doctor` | Show Hermes, optional CodeGraph, Python, Git, and PyYAML status |
| `make doctor-deps` | Install PyYAML with current Python |
| `make community-update` | Clone or fast-forward configured community skill repos |
| `make setup` | Preview profile setup |
| `make apply` | Apply profile setup |
| `make verify` | Verify deployed profiles; source drift is advisory |
| `make verify-strict` | Same checks; fail on canonical source drift |
| `make clean` | Remove Python caches and local `.codegraph/` index |
| `make lint` | Check shell syntax and compile Python files |
| `make test` | Run lint and deterministic Ginflow tests |
| `make verify-test` | Test default versus strict verification drift behavior; requires a dirty canonical file |
| `make harness-test` | Run model-backed blank-project integration test after deterministic harness tests |

## Installation model

Deployed profile state looks like:

```text
~/.hermes/profiles/<name>/
├── SOUL.md -> <repo>/profiles/<name>.SOUL.md
├── config.yaml
├── .env
├── .no-bundled-skills
└── skills/ginflow -> <repo>/skills/ginflow
```

Generated config exposes repo `skills/` and cloned community skills through `skills.external_dirs`. It enables ByteRover memory, configured CLI toolsets, and optional CodeGraph MCP. Missing CodeGraph prints a recommendation; configured but broken CodeGraph makes verification fail.

## Verification semantics

`make verify` checks:

- both profiles exist in account-wide Hermes registry
- `SOUL.md` and local `ginflow` links resolve to this checkout
- generated config avoids legacy global skill paths
- ByteRover memory, model API-key reference, and CodeGraph config exist
- configured skills load and bundled skills are opted out
- profile contracts, Ginflow sections, handoff template, target starter, and five-subsystem static harness agree

Uncommitted changes under canonical setup paths are reported but do not fail normal verification. Use `make verify-strict` for CI or release checks.

Verification does not prove target-project behavior. Target repos own their canonical build/test command and local acceptance evidence.

## Target-project workflow

Open real project repo before implementation. Add `AGENTS.md` or `.hermes.md` for local commands, boundaries, generated-file authorities, and deployment rules. Copy starter when useful:

```bash
cp /path/to/agents-hype/templates/AGENTS.md /path/to/project/AGENTS.md
```

Ginflow requires selected Kanban card for project execution. Card points at real target workspace and links target-local artifacts under `docs/{briefs,specs,plans,handoffs,adrs}`. Completed linked artifacts use path-scoped completion commit baseline; unresolved drift blocks use of affected card as authority.

## Maintenance

```bash
git pull
make community-update
make apply
make verify
make test
```

After `hermes update`, run `make verify` again. Restart active Hermes sessions after config or MCP changes.
