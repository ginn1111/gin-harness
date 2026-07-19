# Ginflow startup adapter for `product/t_ab12`

Yes—create a **temporary normalized JSON adapter**, not a second Kanban card and not a durable competing source of truth. The live Hermes Kanban task remains authoritative. The old harness accepts only a filesystem path via `--card` and then calls `json.loads(args.card.read_text())`, so an adapter file is required unless the caller itself writes the equivalent JSON to a temporary file.

## Exact integration path

```text
Hermes Kanban board `product`
  -> read live task `t_ab12`
  -> normalize task fields + named body sections into a temporary JSON file
  -> derive the real target repository from task.workspace
  -> invoke the external snapshot harness with --target and --card
  -> delete the temporary JSON file
  -> report the project-native verification and Ginflow harness separately
```

Do not copy `validate-harness.py` or the adapter into the target repository. A suitable adapter is:

```json
{
  "id": "t_ab12",
  "title": "<live task title>",
  "objective": "<Objective section from live task body>",
  "scope": ["<items from Scope section>"],
  "acceptance": ["<items from Acceptance section>"],
  "workspace": "<live task workspace field, e.g. dir:/abs/path/to/repo>",
  "status": "<live task status field>",
  "assignee": "<live task assignee field>",
  "links": ["<entries from Links section>"]
}
```

Keep every key, including `links` when it is empty. If the live task is completed/closed and has target-local linked documentation, also copy its existing `artifact_baseline` mapping into the adapter; never synthesize or silently refresh that baseline during resume.

With `TARGET` set to the absolute repository path represented by the card workspace (for example, remove the `dir:` prefix from `dir:/abs/path/to/repo`) and `CARD_JSON` set to the temporary adapter path, run:

```bash
python3 /home/aioz/personal/agents-hype/skills/ginflow-workspace/commit-drift/skill-snapshot/scripts/validate-harness.py \
  --setup-repo '<OLD_SETUP_REPO_ROOT>' \
  --target "$TARGET" \
  --card "$CARD_JSON" \
  --json
```

`<OLD_SETUP_REPO_ROOT>` must be the old setup snapshot root that contains `skills/ginflow/SKILL.md`, `profiles/gintary.SOUL.md`, and `profiles/ginb.SOUL.md`; it is not the target repository. The validator reads those exact paths beneath `--setup-repo`. The supplied snapshot does not define a Hermes CLI command for fetching a live task, so use the available Hermes Kanban API/tool to read board `product`, task `t_ab12`, rather than inventing a shell command.

Before resuming work, run the target repository’s documented canonical verification separately. A harness blocker blocks the affected lifecycle stage; harness output does not replace project verification.

## Where the old harness reads each value

| Required value | Adapter source | Harness use |
|---|---|---|
| `id` | Live task ID `t_ab12` | Required-key check; constructs mandatory brief path `TARGET/docs/briefs/t_ab12.md`; appears in artifact-drift resolution text. |
| `title` | Live task title field | Required-key check. |
| `objective` | `Objective` section of task body | Required-key check. |
| `scope` | `Scope` section of task body | Required-key check and scope-subsystem check. |
| `acceptance` | `Acceptance` section of task body | Required-key check and scope-subsystem check. |
| `workspace` | Live task workspace field | Required-key and scope-subsystem checks. The validator does **not** derive `--target` from it or compare it with `--target`; the adapter must resolve and pass the matching repository explicitly. |
| `status` | Live task status field | Required-key check; values `done`, `completed`, or `closed` activate completed-card artifact drift checks. |
| `assignee` | Live task assignee field | Required-key check. |
| `links` | `Links` section of task body | Required-key check. On completed cards, local links under `docs/` are resolved relative to `--target` and checked against `artifact_baseline`; URL links and paths outside the target are ignored by that drift gate. |

The harness also reads data outside the card adapter:

- `--target` supplies the repository root.
- It reads `.hermes.md` first, otherwise `AGENTS.md`, for local Ginflow routing, boundaries, and a documented canonical verification command.
- It independently requires `TARGET/docs/briefs/<id>.md`; merely putting that path in `links` is not enough.
- For completed cards, it hashes linked target-local `docs/` files and compares them with the card’s `artifact_baseline`.

Treat the adapter as a point-in-time transport artifact: generate it immediately before the harness run from the live task, use it once, and remove it afterward so the live Kanban task remains the only durable card state.