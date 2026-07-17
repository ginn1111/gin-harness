# agents-hype — Install / Update Global Hermes Profiles

Use this repo only for **one-time setup** and **update-time maintenance** of global Hermes profiles.

Profiles installed from this repo:
- `gintary` — planner / dispatcher / escalation sink
- `ginb` — builder / verifier / shipper

---

## 1. Prerequisites

```bash
# Hermes
hermes --version

# Runtime deps
python3 --version
git --version
python3 -m pip install pyyaml
```

---

## 2. Clone repo

```bash
git clone <your-repo-url> agents-hype
cd agents-hype
```

---

## 3. Create repo `.env`

```bash
cp .env.example .env
```

Set:

```bash
GIN_API_KEY=sk-...your-key...
GIN_BASE_URL=https://agents.gin1111.dev/v1
GIN_HOST=agents.gin1111.dev
```

---

## 4. Clone shared community skills

```bash
bash scripts/community-setup.sh --apply
```

---

## 5. Bootstrap profiles

```bash
bash scripts/setup.sh        # dry-run
bash scripts/setup.sh --apply
```

What setup does:
- creates missing profiles
- symlinks `SOUL.md` from repo into deployed profiles
- generates `config.yaml` from template
- keeps profiles sourced from repo-managed skill dirs

---

## 6. Copy per-profile secrets

Important: secret-writing tools redact keys. Use shell copy, not `write_file`.

```bash
for p in gintary ginb; do
  cp .env ~/.hermes/profiles/$p/.env
done
```

---

## 7. Verify

```bash
bash scripts/verify.sh
```

Checks:
- profile exists
- `SOUL.md` symlink target correct
- config uses repo-local skill dirs
- memory provider expected
- skills available
- `.no-bundled-skills` present
- canonical repo files committed

---

## 8. How to use after install

Do **not** use this repo as target project workspace by default.

Instead:
1. open blank project or real project repo
2. use installed global profiles there
3. add project-local `AGENTS.md` or `.hermes.md` if project needs local rules

Global behavior comes from deployed profiles sourced from this repo.
Local project behavior comes from project repo.

---

## 9. Update flow

### Update profile definitions / shared skills

```bash
cd agents-hype
git pull
bash scripts/community-setup.sh --apply
bash scripts/setup.sh --apply
bash scripts/verify.sh
```

### Update Hermes binary

```bash
hermes update
cd agents-hype
bash scripts/verify.sh
```

---

## 10. Blank-project template

Starter template included in this repo:

```bash
cp templates/AGENTS.md /path/to/your-project/AGENTS.md
```

Then edit project-specific commands, constraints, and deployment rules.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| profile missing | setup not applied | `bash scripts/setup.sh --apply` |
| 0 skills enabled | community skills missing | `bash scripts/community-setup.sh --apply` |
| config points to global shared-skills | config stale | rerun `bash scripts/setup.sh --apply` |
| auth fails | wrong or redacted key in `.env` | rewrite `.env`, copy again to each profile |
| `.no-bundled-skills` missing | profile not opted out | `touch ~/.hermes/profiles/<name>/.no-bundled-skills` or recreate profile |

---

## What stays out of repo

Per-machine only:
- `~/.hermes/profiles/<name>/.env`
- session DB / history
- provider auth state
- machine-local secrets

Do not commit those files.
