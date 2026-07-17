# agents-hype — Hermes Solo Delivery Pipeline

Portable Hermes Agent profiles for the **gin delivery pipeline**: `gino → ginb → ginr → gins`.

## Architecture

```
agents-hype/              ← git repo (single source of truth on every machine)
├── profiles/*.SOUL.md    ← canonical personality contracts
├── config/
│   ├── profiles.yaml     ← per-profile overrides (skin, description)
│   └── profile.yaml.tmpl ← config.yaml template ({{PLACEHOLDER}} vars)
├── community/            ← cloned skill repos (git submodule pattern)
│   └── mattpocock-skills/
├── skills/               ← custom gindev skills
├── scripts/
│   ├── setup.sh          ← bootstrap: create profiles + symlink SOUL + gen config
│   ├── verify.sh         ← drift detection against repo
│   └── community-setup.sh← clone/update community skill repos
├── legacy/               ← old scaffold (preserved for reference)
├── Makefile
└── .gitignore
```

Deployed profiles reference repo via **symlinks** (SOUL.md) and **external_dirs** (skills):

```
~/.hermes/profiles/ginb/
├── SOUL.md → /path/to/agents-hype/profiles/ginb.SOUL.md   (symlink)
├── config.yaml            ← generated from template + .env
├── .env                   ← per-machine API keys (never in repo)
└── .no-bundled-skills
```

## Quick start

```bash
# 1. Prerequisites
make doctor

# 2. Setup .env
cp .env.example .env   # edit: GIN_API_KEY, GIN_BASE_URL, GIN_HOST

# 3. Clone community skills
make community-update   # or: scripts/community-setup.sh --apply

# 4. Bootstrap profiles (dry-run first)
make setup              # preview changes
make apply              # create profiles, symlink SOUL, generate configs

# 5. Verify
make verify
```

## Use cases

### Hermes agent version update

Delivery profiles use `--no-skills` → ignore bundled skills. `hermes update` does not affect them. To adopt a new bundled skill: copy it into `skills/` (reviewed, versioned).

### Community asset update

```bash
make community-update         # dry-run: show what would update
scripts/community-setup.sh --apply  # actually git pull
make verify                   # confirm skill counts stable
```

Or pin a specific commit in `community/` if you need stability.

## Migration from legacy scaffold

Old scaffold moved to `legacy/`. The key changes:
- SOUL.md stripped of skill inventories → pure role contracts
- config.yaml generated from template, not hand-edited per machine
- Community skills cloned into repo, tracked via `community-setup.sh`
- Skills loaded via `external_dirs` pointing into repo, not global `~/.hermes/skills/`
