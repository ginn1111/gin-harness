# Doc layout

Use target repo for project work.

Suggested layout:

```text
project/
├── AGENTS.md
├── docs/
│   ├── briefs/
│   ├── specs/
│   ├── plans/
│   ├── handoffs/
│   └── adrs/
└── src/
```

Guidelines:
- follow `artifact-content-guide.md` for artifact boundaries, authority, and content quality
- `docs/briefs/<CARD-ID>.md` for objective, scope, and acceptance
- `docs/specs/<CARD-ID>.md` for behavior and contract detail
- `docs/plans/<CARD-ID>.md` for execution order
- `docs/handoffs/<CARD-ID>.md` for optional exported resume snapshots
- `docs/adrs/` for decisions worth keeping
- skip folders you do not need
- prefer smallest artifact set that keeps handoff clear
- Kanban remains live work state; handoff Markdown is optional

Subsystem mapping:
- instructions: profiles + `ginflow` + local `AGENTS.md`
- state: Kanban card and linked artifacts
- verification: project-native command and card evidence
- scope: card objective/scope/acceptance/workspace
- lifecycle: `ginflow` startup/close/restart and optional export
