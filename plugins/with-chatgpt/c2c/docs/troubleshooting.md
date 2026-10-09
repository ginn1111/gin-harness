# Troubleshooting

First move, always:

```
c2c doctor
```

It checks Node, workspace, bridge, MCP, OAuth and tunnel. It is read-only and
prints the exact repair commands. Run `c2c doctor --repair` to apply bounded
safe repairs (restart the bridge or tunnel) intentionally.

## Common situations

### "Bridge not running"
`c2c start` (or `c2c doctor --repair`). Bridge logs:
`c2c logs`, or verbose: `c2c logs --verbose`.

If doctor says the bridge state is **unknown**, do not start a
second bridge and do not Delete the ChatGPT connector. Wait and run doctor
again. The local process may still be running.

### Everything was quit and ChatGPT can no longer connect
Quitting Hermes / the terminal stops the public address. The next `c2c doctor`
starts a new address and sets `chatgptRepair.needed`. The Skill should tell the
user that the old address expired, then **Delete** THIS workspace's
connector (`chatgptRepair.connectorName`) and create it again with the new
address (never click Reconnect — the old URL is dead). Other workspaces keep
their own connectors so two projects can stay connected at once.

Mint the pairing code only when the ChatGPT Authorize form is on screen
(`c2c pair`). After the connector is recreated, doctor being green is not
enough: the saved ChatGPT conversation must pass `workspace_info` again. If
that old chat still cannot read the workspace, open a new chat in the same
Project (or switch long-chat) and continue there.

Fixed ChatGPT pages for first-time setup and later repair (do not hunt the UI):

- Developer mode: https://chatgpt.com/#settings/Security
- Plugins hub (manage existing connectors): https://chatgpt.com/plugins
- Add a connector:
  https://chatgpt.com/plugins#settings/Connectors?create-connector=true&redirectAfter=%2Fplugins

### Tunnel URL unreachable / ChatGPT says the connector is broken
Same as above: `c2c doctor`, then Delete + recreate THIS workspace's
connector if `chatgptRepair.needed`. Mint a pairing code with `c2c pair` only
when the Authorize form is on screen.
If this workspace uses a stable hostname, doctor sets `namedRepair` instead —
re-login to Cloudflare (`c2c tunnel login`) and doctor again. Do not Delete
the connector; the address did not change.

### I have a Cloudflare domain and want a stable hostname
During first-time setup (or the next coding session, once), say you have a
Cloudflare account and give the domain. Hermes opens a browser for Cloudflare
login, then keeps `c2c-<project>.your-domain.com`. To stay on the temporary
address, say you do not have a domain. Switching later: tell Hermes you want
the stable hostname; it runs `c2c tunnel choose --mode named --zone <domain>`.

### "Pairing code invalid or expired"
Pairing codes are one-time and expire after ~5 minutes. Generate one only
when the ChatGPT Authorize page is ready:

```
c2c pair
```

Older codes become invalid immediately. Do not mint a code during `c2c doctor`.

### Temporary address keeps dropping on a UDP-filtered network
cloudflared defaults to QUIC. If the tunnel reconnects over and over on a
corporate network, set `C2C_TUNNEL_PROTOCOL=http2` and restart the bridge.
Leave it unset to keep cloudflared's default.

### ChatGPT gets 401 on every tool call
The access token expired and refresh failed (e.g. after `c2c unpair` or a
long offline period). Delete THIS workspace's connector if the address also
changed; otherwise run Authorize again in ChatGPT and enter a fresh pairing
code. Never use Reconnect when the public address has been replaced.

### cloudflared is not installed
macOS: `brew install cloudflared`
Windows: `winget install Cloudflare.cloudflared`
Linux: see Cloudflare's package instructions.
The Skill installs this automatically during setup.
If cloudflared is installed in a custom location that is not on `PATH`, set
`C2C_CLOUDFLARED_PATH` to the executable's absolute path before running `c2c`.

### Legacy: Codex sandbox cannot write the state directory
Hermes setup and doctor never touch Codex configuration. If you still run C2C
from Codex, add the state directory explicitly with `c2c sandbox-allow` (legacy
compatibility command; the state directory is `codex-with-chatgpt` under the
platform application-data path).

### Port already in use
Handled automatically: an existing healthy bridge for the same workspace is
reused; anything else makes the bridge pick a free port. Configuration follows
automatically.

### Fixed hostname is configured, but the Named Tunnel does not start on Windows
`cert.pem` and the Named Tunnel credential are different files. `cert.pem`
proves that `cloudflared` has an account certificate; the tunnel still needs
`%USERPROFILE%\.cloudflared\<TUNNEL-UUID>.json` (or the file selected by
`TUNNEL_CRED_FILE`) to run. `c2c doctor --json` reports whether the certificate
is missing, the credential is missing or unreadable, the JSON is invalid, or
the saved Tunnel ID does not match. It never prints credential contents or
repairs the file automatically.

When the diagnostic says the credential is missing, recover the credential for
the existing Tunnel with `cloudflared tunnel token --cred-file` and then run
`c2c doctor` again. Do not paste the generated credential into ChatGPT or a
project file.

### Reading a file returns ACCESS_DENIED_SENSITIVE_FILE
Working as intended: `.env`, keys, credentials and anything matched by
`.c2cignore` are never readable through ChatGPT. `.env.example` is allowed.

### I cannot see Projects in the ChatGPT sidebar
Hover **Chats**, click the … that appears, and choose
**Organize by project**. Then create a project named after
this workspace, with **project-only memory**. Tell Hermes "done" when the
collection page is open (`https://chatgpt.com/g/g-p-…/project`).

### This workspace opened the wrong ChatGPT Project
Do not pick another project by name automatically. Open the collection that
matches this workspace and tell Hermes "found", or say you want the old
long-chat instead. Each workspace has its own Project and its own connector.

### Completely stuck
```
c2c stop
c2c setup
```

re-creates the bridge, tunnel and pairing session from scratch. Existing
authorizations stay valid unless you also ran `c2c unpair`.
