---
name: terminal-browser
description: Use external terminal-browser for explicit ChatGPT workflow steps; this plugin bundles guidance only.
---

# External terminal-browser

`terminal-browser` is an external prerequisite. Hermes with ChatGPT does not install, update, or embed it. `setup` and `doctor` only verify its executable is available.

## Safe workflow

1. Confirm session activation and run local `c2c doctor --json` first.
2. Prefer page-provided WebMCP actions when available.
3. Use snapshot, click, and fill only when no suitable WebMCP action exists.
4. Keep browser action indicator visible during automation and clear it when automation ends.
5. Ask for confirmation before consequential actions: sending messages, changing connectors, deleting/replacing remote objects, or authorizing access.
6. Never enter OAuth tokens, refresh tokens, cookies, browser storage, or bridge admin tokens. Pairing codes are one-use and must be handled only in the documented pairing flow.
7. Reuse saved conversation and workspace connector. Never silently create/switch conversations, churn healthy connectors/tunnels, or operate another workspace's connector.
8. Save C2C checkpoint before browser action. If timeout/interruption occurs, preserve state and resume explicitly.
9. Keep browser work out of `pre_llm_call`; hook only reads bounded local state.
