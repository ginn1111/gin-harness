# Decision

Blocked. No selected Kanban card means ginflow does not permit project execution in `/work/app`, even though bug is clear and small.

## Permitted before card selection

- Classify work as **Implementation** because requirement is clear.
- Size work as **XS/S**.
- Brainstorm or clarify scope.
- Inspect context read-only for task shaping only.
- Choose likely artifact level: brief required; spec and plan optional for clear XS/S work.
- Draft proposed Kanban card content.

## Not permitted

- Create target-repo artifacts, including brief/spec/plan files.
- Run implementation investigation or baseline/project verification.
- Change code or tests.
- Dispatch work to another agent.
- Record implementation progress, verify completion, complete work, or hand off.

## Next action

Create or select one Kanban card, then confirm it contains all required fields: ID, title, objective, scope, acceptance, workspace (`dir:/work/app`), status, assignee, and links. Repair any missing field before execution. Once selected and complete, read local project rules and linked artifacts, inspect git state, run project baseline verification, run external ginflow harness against `/work/app` and selected card, then start implementation.
