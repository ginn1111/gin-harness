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

### "Pairing code invalid or expired"
Pairing codes are one-time and expire after ~5 minutes. Generate one only
when the ChatGPT Authorize page is ready:

```
c2c pair
```

Older codes become invalid immediately. Do not mint a code during `c2c doctor`.

### ChatGPT gets 401 on every tool call
The access token expired and refresh failed (e.g. after `c2c unpair` or a
long offline period). Delete THIS workspace's connector if the address also
changed; otherwise run Authorize again in ChatGPT and enter a fresh pairing
code. Never use Reconnect when the public address has been replaced.

### ngrok is not installed
macOS: `brew install ngrok`
Windows: `winget install ngrok.ngrok`
Linux: see ngrok's package instructions.
Then add your authtoken: `ngrok config add-authtoken <token>` (from dashboard.ngrok.com).
If ngrok is installed in a custom location that is not on `PATH`, set
`C2C_NGROK_PATH` to the executable's absolute path before running `c2c`.

### Legacy: Codex sandbox cannot write the state directory
Hermes setup and doctor never touch Codex configuration. If you still run C2C
from Codex, add the state directory explicitly with `c2c sandbox-allow` (legacy
compatibility command; the state directory is `codex-with-chatgpt` under the
platform application-data path).

### Port already in use
Handled automatically: an existing healthy bridge for the same workspace is
reused; anything else makes the bridge pick a free port. Configuration follows
automatically.

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
