# Ginflow artifact repository

Run commands from the repository root.

## Prerequisites

- Python 3
- POSIX shell
- Make
- Git

Optional:

- CodeGraph for workspace navigation and health reporting
- Hermes Agent if you want to consume the optional `skills/ginflow` skill or `plugins/ginflow-gate` adapter

The repository does not require a Hermes installation, Hermes profile, profile directory, profile manifest, or profile configuration.

## Validate the repository

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
make setup                                # preview currently active profile
make setup PROFILES="profile-a"          # preview named profile
make apply PROFILES="profile-a"
make verify PROFILES="profile-a"
```

### Install Ginflow skill and with-chatgpt plugin

Use the dedicated installer. The skill is shared; the plugin goes into Hermes profiles:

```bash
make install                              # plugin into every Hermes profile
make install PROFILES="profile-a profile-b"   # plugin into selected profiles only
```

This copies `skills/ginflow`, including `lib/harness_core.py`, once to `~/.agents/skills/ginflow`, and copies `plugins/with-chatgpt` into `~/.hermes/profiles/<profile>/plugins/with-chatgpt` for every profile that has a `config.yaml` (or only the profiles named in `PROFILES`). It does not modify profile config. Installer ownership is recorded in setup-repo-root `.ginflow-install.json`, which is gitignored.

Remove only installer-owned files with:

```bash
make uninstall
```

Uninstall restores installer backups and refuses to delete paths changed after installation. Resolve reported conflicts manually, then rerun `make uninstall`.

Setup requires existing profiles. It adds only:

- Ginflow skill
- setup-repo and optional community skill directories
- `ginflow-gate` plugin
- CodeGraph MCP and its toolset
- common CLI toolsets needed by harness/workflow

### Hermes with ChatGPT plugin

`make install` installs standalone plugin `with-chatgpt` at
`~/.hermes/profiles/<profile>/plugins/with-chatgpt` for every Hermes profile. Hermes discovers it through
native plugin APIs. It registers `with-chatgpt:c2c` and
`with-chatgpt:terminal-browser` skills plus the CLI command
`hermes with-chatgpt <setup|doctor|enable|disable|status|pair|stop>`.

The installer excludes `node_modules`, `dist`, and `.tooling`. Build the C2C
runtime in the installed copy (`pnpm install && pnpm build` under
`plugins/with-chatgpt/c2c`) before `setup`; `setup` and `doctor` report a
missing build instead of claiming readiness.

Collaboration stays disabled until the current Hermes session is explicitly
enabled. `pre_llm_call` adds only bounded local workflow state, never secrets,
files, diffs, logs, or mutation. Hook failures fail open. Plugin `doctor` is
read-only by default; pass `--repair` only when bridge/tunnel repair is
intentional. Normal setup and doctor do not edit Codex configuration; the legacy compatibility command is explicit only. Existing
C2C names, state, auth, pairing, read-only MCP, and protocol remain unchanged.

Validate without enabling collaboration:

```bash
hermes plugins validate plugins/with-chatgpt
make with-chatgpt-test
```

#### Step-by-step: install and use for an agent

Prerequisites: Node.js 20 or newer, `terminal-browser` installed separately, an existing Hermes profile. Steps 1-4 and 8 are safe for an agent to run. Steps 5-7 start services or change session state; run them only when the user asks. Live ChatGPT, `terminal-browser`, and `cloudflared` flows are not covered by repository tests.

1. Install (repo root). Skill goes to `~/.agents/skills/ginflow`; plugin goes to all Hermes profiles. Add `PROFILES="<profile>"` to limit the plugin:

   ```bash
   make install
   ```

2. Build the C2C runtime in the installed copy:

   ```bash
   cd ~/.hermes/profiles/<profile>/plugins/with-chatgpt/c2c
   CI=true pnpm install && pnpm build
   ```

3. Enable the plugin, then restart active Hermes sessions:

   ```bash
   hermes plugins enable with-chatgpt
   hermes plugins list
   ```

4. Check prerequisites (read-only; never starts anything):

   ```bash
   hermes with-chatgpt setup --workspace /abs/path/to/target-repo
   ```

   Read `ready` and `next_steps` in the result. Use the target repository as `--workspace`, not this repository.

5. Start the bridge and tunnel (explicit; first run asks the user to choose AI-automated or guided manual setup):

   ```bash
   cd ~/.hermes/profiles/<profile>/plugins/with-chatgpt/c2c
   node dist/cli/index.js setup --workspace /abs/path/to/target-repo
   ```

6. Pair with ChatGPT once the user has the Authorize form open:

   ```bash
   hermes with-chatgpt pair --workspace /abs/path/to/target-repo
   ```

7. Enable collaboration for the current session (off by default, per session). Pass the session ID explicitly if `$HERMES_SESSION_ID` is empty:

   ```bash
   hermes with-chatgpt enable --session-id "$HERMES_SESSION_ID"
   ```

8. Day to day (add `--json` for stable JSON):

   ```bash
   hermes with-chatgpt status --workspace /abs/path/to/target-repo
   hermes with-chatgpt doctor              # read-only
   hermes with-chatgpt doctor --repair     # only when repair is intended
   hermes with-chatgpt disable --session-id "$HERMES_SESSION_ID"
   hermes with-chatgpt stop                # stops a healthy, authenticated bridge
   ```

Bridge state `unknown` is not `stopped`: run `doctor` and never start a second bridge. ChatGPT gets read-only MCP access to the workspace only.

Uninstall checks both Ginflow and `with-chatgpt` hashes, preserves conflicts, and
restores backups. Profile identity, secrets, sessions, memories, runtime, and
C2C state stay outside installer-owned paths.

The plugin is opt-in; installation does not enable collaboration. Setup also
installs the `with-chatgpt` plugin when using this installer.

Setup preserves profile-owned `SOUL.md`, `distribution.yaml`, provider/model identity, secrets, memories, sessions, auth, cron, and release metadata.

Setup resolves profiles from `$HERMES_PROFILES_DIR` when set. Otherwise it uses `$HERMES_REAL_HOME/.hermes/profiles`, falling back to real user home. This avoids profile-session `$HOME` paths when wiring another profile.

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
make verify
```

`make test` runs the standalone core, artifact-guidance, Kanban-harness, plugin, recovery, and installation-independent guidance checks. `make verify` runs the Ginflow harness without requiring a target workspace or Hermes profile.

## Consume the artifacts

Use the repository directories directly or copy the required artifacts into another project or runtime:

- `core/ginflow-core/` — reusable routing and validation primitives
- `templates/` — target-project starter context and artifact templates
- `skills/ginflow/` — optional Hermes-compatible workflow skill
- `plugins/ginflow-gate/` — optional Hermes-compatible completion gate
- `skills/ginflow/scripts/` — portable validation and test helpers

For a target project, copy `templates/AGENTS.md` into the target repository and adapt its local commands, boundaries, and canonical verification path.

## Optional Hermes integration

Hermes integration is deliberately outside this repository's runtime boundary. Install or configure Hermes using the official Hermes documentation, then consume the optional skill and plugin according to that runtime's integration mechanism.

This repository does not:

- discover or select Hermes profiles;
- mutate profile configuration;
- install or uninstall profile integrations;
- manage profile identity, secrets, sessions, memories, cron, or provider settings; or
- require Hermes to run its core validation suite.

## Target-project workflow

Do not implement product work in this repository. Agents should use the Ginflow workflow against the real target repository, with the target project's local rules and canonical verification command.

The target project owns:

- product code and tests;
- local `AGENTS.md` / `.hermes.md` rules;
- Kanban-linked Spec, Plan, ADR, and Handoff artifacts; and
- product verification and delivery decisions.

The Ginflow skill and plugin remain optional adapters. They do not replace the target project's own toolchain or verification.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `make` is missing | Install Make from your operating system toolchain |
| Python dependency error | Use Python 3 and rerun `make lint` |
| CodeGraph warning | Install and initialize CodeGraph only if workspace navigation is needed |
| Hermes integration needed | Configure Hermes separately, then consume the optional skill/plugin artifacts |
| Target verification is unknown | Add the canonical command to the target project's local rules |
