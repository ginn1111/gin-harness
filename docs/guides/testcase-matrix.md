# Testcase Matrix

`make test` runs the repository’s deterministic checks in dependency order. The current run passed with exit code `0`.

| Test case | Related modules / package files | Behavior and flow | Expected output | Current snapshot |
|---|---|---|---|---|
| `lint` | `scripts/*.sh`, `scripts/*.py`, `skills/ginflow/scripts/*.sh`, `skills/ginflow/scripts/*.py` | Runs shell syntax checks, then Python compilation checks. | No syntax errors. | `lint ok` |
| `setup-test` | `Makefile`, `scripts/setup.sh` | Creates temporary Hermes profiles; verifies active-profile selection and `make apply` configuration. | Only the active profile is integrated; config is valid. | `setup active-profile default and null config test ok` |
| `harness-core-test` | `skills/ginflow/lib/harness_core.py`, `skills/ginflow/scripts/test-harness-core.py` | Tests card-body parsing and startup-gate decisions. | Card fields parse correctly; valid cards route to `ready_to_start`. | `ginflow harness core test passed`<br>`ginflow startup gate test passed` |
| `artifact-guidance-test` | `skills/ginflow/SKILL.md`, `skills/ginflow/references/*.md`, `skills/ginflow/templates/*.md`, `skills/ginflow/evals/evals.json`, `templates/AGENTS.md` | Validates documentation paths, required policy sections, evaluation IDs, warning coverage, and legacy-path removal. | Documentation and evaluation contracts are consistent. | `ginflow artifact guidance test passed` |
| `kanban-board-isolation-test` | `scripts/test-kanban-board-isolation.py`, selected Kanban test files | Confirms live Kanban tests use the dedicated `gin-harness-testing` board. | No test command can modify the active board. | `Kanban test board isolation passed` |
| `kanban-harness-test` | `skills/ginflow/scripts/validate-harness.py`, `skills/ginflow/lib/harness_core.py`, `skills/ginflow/scripts/test-kanban-harness.py` | Exercises missing-card blockers, valid cards, linked documents, optional-tool states, and live cards. | Correct pass, warning, and blocker decisions. | `ginflow Kanban harness test passed` |
| `ginflow-gate` routing | `plugins/ginflow-gate/routing.py`, `core/ginflow-core/routing.py`, `skills/ginflow/lib/harness_core.py`, `plugins/ginflow-gate/test_ginflow_gate.py` | Tests workspace/status routing, Ginflow skill detection, live-card routing, and blocked-route reporting. | Routing is deterministic and only active when Ginflow is loaded. | `PASS: workspace/status routes`<br>`PASS: no ginflow → routing not called`<br>`PASS: ginflow active → routing called`<br>`PASS: live temporary project/card routing`<br>`PASS: live temporary next-card doc validation`<br>`PASS: blocked route reports metadata without execution`<br>`ginflow routing test passed` |
| `ginflow-gate` completion rejection | `plugins/ginflow-gate/gate.py`, `plugins/ginflow-gate/test_ginflow_gate.py` | Validates completion metadata, linked-document state, workspace, and artifact baseline. | Invalid completion requests are rejected. | `ginflow gate rejection test passed` |
| `blocker-reporting-test` | `plugins/ginflow-gate/blocker_reporting.py`, `plugins/ginflow-gate/test_blocker_reporting.py` | Validates blocker-event structure, safe comments, supported kinds, evidence, and timestamps. | Invalid events fail; the safe blocker contract passes. | `blocker reporting contract passed` |
| `recovery-policy-test` | `plugins/ginflow-gate/recovery_policy.py`, `plugins/ginflow-gate/blocker_reporting.py`, `plugins/ginflow-gate/test_recovery_policy.py` | Tests bounded retries, retry exhaustion, non-recoverable blockers, mismatches, and idempotency. | Recoverable blockers retry up to three times; unsafe cases remain blocked or notify a human. | `bounded recovery policy passed` |
| `recovery-test` | `plugins/ginflow-gate/recovery.py`, `plugins/ginflow-gate/test_recovery.py` | Tests recovery decisions, exclusive leases, notification delivery, and duplicate suppression. | Recovery is serialized, bounded, and idempotent. | `blocked recovery policy passed` |
| `guidance-test` | `skills/ginflow/SKILL.md`, `skills/ginflow/references/kanban-guide.md`, `skills/ginflow/scripts/test-guidance.sh` | Confirms watcher, read-only, heartbeat, terminal-state, and non-interactive guidance. | Required operational guidance is present. | `ginflow guidance ok` |
| `install-test` | `scripts/install.sh`, `plugins/ginflow-gate/`, `core/ginflow-core/`, `skills/ginflow/` | Tests installation, config preservation, idempotent reinstall, conflict protection, and clean uninstall. | Install is complete, repeatable, conflict-safe, and reversible. | `install/uninstall tests passed` |

## Result

```text
make test: PASSED
exit code: 0
```

The suite covers the Ginflow core library, routing core, completion gate, blocker/recovery package, documentation assets, setup/install scripts, and Kanban test isolation.
