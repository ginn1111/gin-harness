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
- keep the target-specific drift contract in `AGENTS.md` or `.hermes.md`: canonical command, local authorities, generated-file relationships, and remediation order
- `docs/briefs/<CARD-ID>.md` for objective, scope, and acceptance
- `docs/specs/<CARD-ID>.md` for behavior and contract detail
- `docs/plans/<CARD-ID>.md` for execution order
- `docs/handoffs/<CARD-ID>.md` for optional exported resume snapshots
- `docs/adrs/` for decisions worth keeping
- skip folders you do not need
- prefer smallest artifact set that keeps handoff clear
- Kanban remains live work state; handoff Markdown is optional

`<CARD-ID>` denotes the stable human-facing work key chosen before Hermes creates its internal `t_...` task ID. Keep the key in the title and links; use the generated task ID only for Kanban API/CLI calls.

Subsystem mapping:
- instructions: profiles + `ginflow` + local `AGENTS.md`
- state: Kanban card and linked artifacts
- verification: project-native command and card evidence
- scope: card objective/scope/acceptance/workspace
- lifecycle: `ginflow` startup/close/restart and optional export
