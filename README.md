# gin-harness

Hermes native harness system.

This repo contains no profile identity, profile manifest, profile registry, provider config, or distribution package. Profiles are installed, exported, imported, and updated by Hermes itself. This repo only plugs shared skills, Ginflow harness, MCPs, plugins, and toolsets into profiles selected at runtime.

## Ownership

| Owner | Content |
|---|---|
| Hermes profile distribution | `SOUL.md`, `distribution.yaml`, native `config.yaml` defaults, profile skills/cron, version, release source |
| This setup repo | `skills/ginflow`, harness/tests, optional community skills, CodeGraph MCP/tool wiring, target-project starter |
| Target project | code, tests, `AGENTS.md` / `.hermes.md`, briefs/specs/plans/handoffs |

No profile names or profile package files belong here.

## Hermes-native profile lifecycle

```bash
# Install profile from its distribution repository
hermes profile install github.com/owner/profile --alias

# Update distribution-owned files; preserve user data and config overrides
hermes profile update <profile>

# Include updated native config defaults when intentionally requested
hermes profile update <profile> --force-config

# Portable archive flow
hermes profile export <profile> -o <profile>.tar.gz
hermes profile import <profile>.tar.gz
```

Hermes owns update safety: `SOUL.md`, skills, cron, and MCP distribution files update from recorded source; memories, sessions, auth, and `.env` remain local.

## Plug integrations into profiles

```bash
make doctor
make community-update              # optional community skill checkout
make setup                         # preview currently active profile
make setup PROFILES="profile-a"   # preview named profile
make apply PROFILES="profile-a"   # apply integration wiring
make verify PROFILES="profile-a"
make test
```

`make apply` requires profiles already installed. It does not create profiles and does not touch `SOUL.md`, `distribution.yaml`, model/provider identity, `.env`, memory, sessions, cron, or release metadata.

Profile location defaults to `$HERMES_REAL_HOME/.hermes/profiles`, or real user home when `HERMES_REAL_HOME` is unset. Set `HERMES_PROFILES_DIR` to override it, useful for test or nonstandard installs.

Applied integrations:

- `skills/ginflow` linked into each selected profile
- setup repo `skills/` exposed through `skills.external_dirs`
- optional community skills exposed when checkout exists
- `plugins/ginflow-gate` linked and enabled; existing plugin entries remain untouched
- CodeGraph MCP registered as `codegraph serve --mcp`
- required CLI toolsets enabled, including `mcp-codegraph`
- one-time native `config.yaml.bak.integration` backup

Restart profile sessions after apply.

## Repository map

| Path | Purpose | Docs |
|---|---|---|
| `skills/ginflow/` | Shared workflow, templates, validator, tests | `skills/ginflow/SKILL.md` |
| `skills/ginflow-workspace/` | Eval evidence, including gate rejection and independent-profile coverage | inline |
| `plugins/ginflow-gate/` | Blocking Kanban completion policy | source code |
| `Makefile` | Active-profile default selection plus setup, verification, and test entry points | inline comments |
| `scripts/setup.sh` | Integration preview/apply for active or explicitly named profiles | `INSTALL.md` §3 |
| `scripts/verify.sh` | Generic integration and harness verification | `INSTALL.md` §3 |
| `scripts/test-setup.sh` | Regression test for active-profile-only default selection | source code |
| `scripts/community-setup.sh` | Optional community skill checkout | source code |
| `scripts/detect-skill-drift.py` | Shared-skill shadow detector utility | source code |
| `templates/AGENTS.md` | Target-project starter | `templates/AGENTS.md` |
| `INSTALL.md` | Full native-profile and integration guide | `INSTALL.md` |

## Agent workflow

Agents using this setup repo must load and follow `ginflow` for target-project startup, task shaping, execution, completion, and handoff. Do not use this setup repo as target-project workspace. Target-project mutable work requires a selected, complete Kanban card and linked local artifacts.

## Verification boundary

`make verify PROFILES="..."` checks selected profiles exist and retain profile-owned identity files while setup integrations work. It does not compare profile identity or distribution metadata against this repo.

Without `PROFILES`, setup/apply/verify target only profile marked active by `hermes profile use <name>`. Profiles stay independent; harness does not coordinate or hand work between them.

`make verify-strict PROFILES="..."` additionally fails on uncommitted setup integration changes.

Target-project behavior remains separate. Run project-native verification in target repo.

## Maintenance

```bash
git pull
make community-update
make apply PROFILES="profile-a"
make verify PROFILES="profile-a"
make test
```

Profile updates stay independent:

```bash
hermes profile update <profile>
make apply PROFILES="<profile>"    # re-plug setup integrations if update replaced links/config
make verify PROFILES="<profile>"
```
