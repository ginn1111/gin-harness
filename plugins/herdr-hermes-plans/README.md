# Hermes Plans for Herdr

Pick a Hermes Plan Mode Markdown file and submit its full contents to the
agent pane that opened the popup. Requires Herdr 0.9.5+ and Python 3.11+
with curses (Linux/macOS); no packages to install.

From this repository:

```sh
herdr plugin link "$PWD/plugins/herdr-hermes-plans"
```

Focus an agent pane, then choose **Hermes: send plan to agent** from Herdr's
plugin actions. The action can also be invoked with:

```sh
herdr plugin action invoke pick --plugin gin.hermes-plans
```

The target is the pane focused when the action is invoked. Plans come from
that agent's working directory's `.hermes/plans/`, including `approved/`.
No plans are read from other workspaces or from `docs/plans/`.

- Up/Down selects a file; preview shows its text.
- Left/Right scrolls preview vertically by a page.
- Enter submits the displayed file's complete text once and closes popup.
- Escape cancels without sending anything.

Agent must be idle or done and running in foreground when submitting.
Changed sessions, processes, terminals, or directories reject submission.
Herdr does not offer an atomic compare-session-and-submit API: these checks
run immediately before its own agent-aware prompt command. Do not replace
or suspend the agent during submission.

Files must be regular UTF-8 Markdown, nonempty, without terminal control
characters, and no larger than 64 KiB. Symlinks are rejected. Text is passed
as a literal argument, never evaluated by a shell. Full text is sent even
when preview is clipped by popup width. This sends text; it does not grant
Hermes Plan Mode approval or bypass Hermes approval controls.

Delivery errors close after acknowledgement and are never retried. Check
the agent before retrying manually; a timeout may occur after delivery.
Action startup errors appear as a Herdr notification and in plugin logs.

```sh
make herdr-plan-test
make lint && make test
```

The focused check uses a fake Herdr CLI and real pseudo-terminal. It sends
no messages to live agents. To unlink:

```sh
herdr plugin unlink gin.hermes-plans
```
