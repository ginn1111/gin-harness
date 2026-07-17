# Gin Delivery Pipeline — New Installation Guide

Set up 2 Hermes agent profiles from scratch on a new machine: `gintary` (planner/dispatcher/escalation sink) → `ginb` (builder, self-reviewer, shipper).

---

## 1. Prerequisites

```bash
# Hermes agent
pip install hermes-agent
hermes update

# Runtime deps
python3 -m pip install pyyaml

# Verify
hermes --version   # v0.18.2+
python3 --version  # 3.11+
git --version
```

---

## 2. Clone the repo

```bash
git clone <your-repo-url> agents-hype
cd agents-hype
```

This repo contains:

```
agents-hype/
├── profiles/*.SOUL.md    ← role contracts (symlinked into deployed profiles)
├── config/
│   ├── profiles.yaml     ← per-profile overrides
│   └── profile.yaml.tmpl ← config.yaml template
├── scripts/
│   ├── setup.sh           ← bootstrap profiles
│   ├── verify.sh          ← drift detection
│   └── community-setup.sh ← clone skill repos
├── skills/               ← custom skills (populate with your own)
├── community/            ← cloned community skill repos
├── Makefile
└── README.md
```

---

## 3. Create `.env`

```
GIN_API_KEY=sk-...your-key...
GIN_BASE_URL=https://agents.gin1111.dev/v1
GIN_HOST=agents.gin1111.dev
```

- `GIN_API_KEY` — API key for your LLM provider
- `GIN_BASE_URL` — OpenAI-compatible endpoint base
- `GIN_HOST` — hostname matching the `custom_providers` name in config template

Without `.env`, the setup script uses defaults (agents.gin1111.dev) but auth will fail.

---

## 4. Clone community skills

```bash
# Dry-run
bash scripts/community-setup.sh

# Apply — clones mattpocock/skills into community/
bash scripts/community-setup.sh --apply
```

Expected: `community/mattpocock-skills/skills/` with ~80+ skill dirs.

To add more repos later, edit `scripts/community-setup.sh` and add entries to the `REPOS` array.

---

## 5. Populate custom skills (optional)

Your gindev-origin skills go into `skills/`. These are loaded via `external_dirs` in config.

If you have existing skills at `~/.hermes/skills/`, copy the ones you want:

```bash
mkdir -p skills/software-development
cp -r ~/.hermes/skills/software-development/my-skill skills/software-development/
```

Only the skills you explicitly copy will be available — profiles don't inherit the global `~/.hermes/skills/` dir.

---

## 6. Bootstrap profiles

```bash
# Dry-run — see what would change
bash scripts/setup.sh

# Apply — creates profiles, symlinks SOUL.md, generates config.yaml
bash scripts/setup.sh --apply
```

What happens:

| Step | Action |
|------|--------|
| Profile creation | `hermes profile create <name> --no-skills` (skips if exists) |
| SOUL.md | Symlinked: `~/.hermes/profiles/<name>/SOUL.md → repo/profiles/<name>.SOUL.md` |
| config.yaml | Generated from template with `{{PLACEHOLDER}}` replaced by `.env` values |
| `.no-bundled-skills` | Preserved (set at profile creation) |
| external_dirs | Points to `repo/community/mattpocock-skills/skills` + `repo/skills` |

Old SOUL.md and config.yaml are backed up with `.bak.<timestamp>` suffix.

---

## 7. Copy API keys into profiles

```bash
for p in gintary ginb; do
  cp .env ~/.hermes/profiles/$p/.env
done
```

Each profile needs its own `.env` because Hermes scopes environment per-profile.

---

## 8. Verify

```bash
bash scripts/verify.sh
```

Expected output:

```
✅ gintary: exists
✅ gintary: SOUL.md symlinked to repo
✅ gintary: config.yaml uses repo-local paths
✅ gintary: memory provider=holographic
...
✅ ginb: exists
✅ ginb: SOUL.md symlinked to repo
✅ ginb: config.yaml uses repo-local paths
✅ ginb: memory provider=byterover
...
✅ All checks passed.
```

---

## 9. Use the pipeline

### Run a delivery

Work starts in `gintary` profile. Describe the work:

```bash
# Use gintary as your daily driver profile
hermes chat
```

gintary plans and dispatches Kanban tasks to `ginb`.

Or assign a small task directly:

```bash
hermes -p ginb chat
> delivery_id: DM-42 | brief: docs/dm-42.md | scope: src/ | size: XS | acceptance: button changes color
```

### Pipeline flow

```
gintary  →  ginb  →  done
   │           │
   │ plan/     │ build +
   │ decompose │ self-review +
   │           │ ship
   │           │
   └─ blocks ←─┘
        ↓
     human
```

- ginb reads `memories/USER.md` + `memories/MEMORY.md` before starting work
- ginb self-verifies against acceptance criteria, records evidence
- ginb blocks to gintary when stuck, unclear, or blocked
- No separate reviewer or shipper profile

---

## 10. Updating

### Hermes agent

```bash
hermes update
```

Delivery profiles use `--no-skills` — bundled skills are ignored. No impact.

### Community skills (mattpocock, etc.)

```bash
bash scripts/community-setup.sh --apply   # git pull each repo
bash scripts/verify.sh                      # check skill counts stable
```

### Repo changes (SOUL.md, config)

Pull the repo, re-run setup:

```bash
git pull
bash scripts/setup.sh --apply  # updates SOUL.md symlinks + regenerates config
bash scripts/verify.sh
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `setup.sh` writes to wrong `~/.hermes` | Running inside a sandboxed session | Fixed by `REAL_HOME` resolution in script — verify with `getent passwd` |
| 0 skills enabled | `external_dirs` missing or community skills not cloned | Run `scripts/community-setup.sh --apply` |
| `config.yaml` references `shared-skills` | Was not regenerated from template | Re-run `scripts/setup.sh --apply` |
| Profile missing from `hermes profile list` | Not created yet | `hermes profile create <name> --no-skills` |
| `.no-bundled-skills` missing | Profile created with bundled skills | `hermes -p <name> skills opt-out` |
| Byterover memory not working | Auth not configured | `cd ~/.hermes/shared-skills/byterover && node scripts/auth.mjs` |

---

## What stays per-machine (not in repo)

| Artifact | Location | Purpose |
|----------|----------|---------|
| `.env` | `~/.hermes/profiles/<name>/.env` | API keys, tokens |
| `memories/` | `~/.hermes/profiles/<name>/memories/` | USER.md, MEMORY.md (conventions) |
| `state.db` | `~/.hermes/profiles/<name>/` | Session history |
| ByteRover auth | `~/.hermes/shared-skills/byterover/` | Memory provider credentials |

None of these are in the repo. On a new machine, create them after running `setup.sh`.
