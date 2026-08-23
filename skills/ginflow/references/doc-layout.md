# Doc layout

Use target repo for project work.

Suggested layout:

```text
project/
├── AGENTS.md
├── docs/

│   ├── specs/
│   ├── plans/
│   ├── handoffs/
│   └── adrs/
└── src/
```

Guidelines:
- follow `artifact-content-guide.md` for artifact boundaries, authority, and content quality
- put artifact metadata in YAML frontmatter at byte 0; use `status`, `size`, `scope`, and `owner` for specs and plans
- keep lifecycle metadata in the header rather than duplicating `Status:` prose in the document body
- keep the target-specific drift contract in `AGENTS.md` or `.hermes.md`: canonical command, local authorities, generated-file relationships, and remediation order

- Target Spec artifact for behavior and contract detail
- Target Plan artifact for execution order
- Target Handoff artifact for optional exported resume snapshots
- Target ADR location for decisions worth keeping
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
