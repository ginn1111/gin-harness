# agents-hype

Integration kit for Hermes-native profiles.

This repo contains no profile identity, profile manifest, profile registry, provider config, or distribution package. Profiles are installed, exported, imported, and updated by Hermes itself. This repo only plugs shared skills, Ginflow harness, MCPs, plugins, and toolsets into profiles selected at runtime.

## Ownership

| Owner | Content |
|---|---|
| Hermes profile distribution | `SOUL.md`, `distribution.yaml`, native `config.yaml` defaults, profile skills/cron, version, release source |
| This setup repo | `skills/ginflow`, harness/tests, optional community skills, `herdr-agent-state`, CodeGraph MCP/tool wiring, target-project starter |
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
make setup PROFILES="profile-a profile-b"   # preview
make apply PROFILES="profile-a profile-b"   # apply integration wiring
make verify PROFILES="profile-a profile-b"
make test
```

`make apply` requires profiles already installed. It does not create profiles and does not touch `SOUL.md`, `distribution.yaml`, model/provider identity, `.env`, memory, sessions, cron, or release metadata.

Applied integrations:

- `skills/ginflow` linked into each selected profile
- setup repo `skills/` exposed through `skills.external_dirs`
- optional community skills exposed when checkout exists
- `plugins/herdr-agent-state` linked and enabled
- CodeGraph MCP registered as `codegraph serve --mcp`
- required CLI toolsets enabled, including `mcp-codegraph`
- one-time native `config.yaml.bak.integration` backup

Restart profile sessions after apply.

## Repository map

| Path | Purpose |
|---|---|
| `skills/ginflow/` | Shared workflow, templates, validator, tests |
| `plugins/herdr-agent-state/` | Optional lifecycle-state plugin |
| `scripts/setup.sh` | Generic integration preview/apply for named existing profiles |
| `scripts/verify.sh` | Generic integration and harness verification |
| `scripts/community-setup.sh` | Optional community skill checkout |
| `scripts/detect-skill-drift.py` | Shared-skill shadow detector utility |
| `templates/AGENTS.md` | Target-project starter |
| `INSTALL.md` | Full native-profile and integration guide |

## Verification boundary

`make verify PROFILES="..."` checks selected profiles exist and retain profile-owned identity files while setup integrations work. It does not compare profile identity or distribution metadata against this repo.

`make verify-strict PROFILES="..."` additionally fails on uncommitted setup integration changes.

Target-project behavior remains separate. Run project-native verification in target repo.

## Maintenance

```bash
git pull
make community-update
make apply PROFILES="profile-a profile-b"
make verify PROFILES="profile-a profile-b"
make test
```

Profile updates stay independent:

```bash
hermes profile update <profile>
make apply PROFILES="<profile>"    # re-plug setup integrations if update replaced links/config
make verify PROFILES="<profile>"
```
