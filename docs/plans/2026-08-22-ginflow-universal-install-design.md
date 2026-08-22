# Ginflow Universal Installation Design

**Status: approved design**
**Date:** 2026-08-22

## Objective

Add a dedicated setup-repository installer that copies the Ginflow universal skill and plugin integration into every installed Hermes profile, with safe uninstall support. Keep the existing profile setup flow stable.

## Decisions

- Script: `scripts/install.sh`.
- Commands: `scripts/install.sh install` and `scripts/install.sh uninstall`.
- Universal skill destination: `~/.agent/skills/ginflow`.
- Universal skill installation method: copy, not symlink.
- Plugin installation method: copy, not symlink.
- Profile scope: discover and process all profiles returned by `hermes profile list`.
- Ownership manifest: `.ginflow-install.json` at setup-repo root.
- Manifest is local-only and added to `.gitignore`.
- Uninstall removes only installer-owned paths, restores installer-created backups, and preserves post-install user edits as conflicts.

## Installation flow

1. Resolve setup-repo root, real home, profiles directory, and universal-agent skill directory.
2. Require `hermes` and `python3`.
3. Discover all installed profiles from `hermes profile list`.
4. Validate every profile has a native `config.yaml` before mutating any destination.
5. Copy `skills/ginflow` to `~/.agent/skills/ginflow`.
6. Copy `plugins/ginflow-gate` into each profile's `plugins/ginflow-gate` directory.
7. Update each profile's `config.yaml` without removing unrelated settings:
   - expose the setup-repo skill directory through `skills.external_dirs`;
   - enable `ginflow-gate`;
   - preserve existing MCP, toolset, plugin, and profile-owned settings.
8. Record source fingerprints, destination fingerprints, profile paths, config backups, and ownership metadata in `.ginflow-install.json`.

Copies use temporary destinations and atomic replacement where possible. Existing destinations are backed up and recorded before replacement. Unexpected symlinks are not followed.

## Uninstallation flow

1. Load `.ginflow-install.json`.
2. For each managed skill/plugin copy, compare current content with the recorded installed fingerprint.
3. Remove unchanged installer-owned copies and restore recorded backups.
4. For changed paths, preserve user edits and report a conflict.
5. Restore a profile config only when it still matches the installer's expected post-install state; otherwise preserve it and report the profile.
6. Remove the manifest only after cleanup succeeds without unresolved ownership errors.
7. Return non-zero when conflicts remain.

The manifest contains paths, methods, fingerprints, and backup metadata only. It must not contain credentials, tokens, `.env` values, profile identity, or runtime state.

## Error handling

- Missing dependencies, invalid profile output, no profiles, or missing profile config fail before mutation.
- Installation is all-or-nothing across discovered profiles.
- Uninstall is best-effort and reports every conflict.
- Repeated install is idempotent: no duplicate config entries and stable ownership state.

## Testing

Add `scripts/test-install.sh` using temporary homes, temporary profile directories, and fake `hermes` commands. Cover:

- all-profile discovery and copy installation;
- universal skill copy;
- profile config updates;
- preflight failure with no mutation;
- existing destination backups;
- successful uninstall and backup restoration;
- changed-path uninstall conflict protection;
- repeated-install idempotency.

Add `install`, `uninstall`, and `install-test` Makefile targets. Include `install-test` in `make test`. Document commands in `README.md` and `INSTALL.md`.

## Boundaries

The installer must not modify Hermes profile identity, `SOUL.md`, distribution manifests, provider/model settings, secrets, memories, sessions, auth, cron, or remote repositories. Existing `scripts/setup.sh` remains available for explicit-profile compatibility.
