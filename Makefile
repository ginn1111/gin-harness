.PHONY: verify doctor community-update clean lint test harness-test artifact-guidance-test kanban-harness-test harness-core-test plugin-test status-transition-test guidance-test

status-transition-test:
	bash skills/ginflow/scripts/test-status-transition.sh

# === Pre-flight ===
doctor:
	@echo "=== CodeGraph ==="; command -v codegraph && codegraph --version || echo "MISSING"
	@echo "=== Python ==="; python3 --version
	@echo "=== Git ==="; git --version

# === Standalone validation ===
verify:
	python3 skills/ginflow/scripts/validate-harness.py --setup-repo . --json

# === Community assets ===
## Clone/pull community skill repos
community-update:
	./scripts/community-setup.sh --apply

# === Hygiene ===
## Remove generated local files
clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
	rm -rf .codegraph

lint:
	bash -n scripts/*.sh
	@if compgen -G 'scripts/*.py' >/dev/null; then python3 -m py_compile scripts/*.py; fi
	bash -n skills/ginflow/scripts/*.sh
	python3 -m py_compile skills/ginflow/scripts/*.py
	@echo "lint ok"

## Run deterministic repository tests
test: lint harness-core-test artifact-guidance-test kanban-harness-test plugin-test guidance-test

harness-core-test:
	python3 skills/ginflow/scripts/test-harness-core.py

plugin-test:
	python3 plugins/ginflow-gate/test_ginflow_gate.py
	python3 plugins/ginflow-gate/test_blocker_reporting.py
	python3 plugins/ginflow-gate/test_recovery_policy.py
	python3 plugins/ginflow-gate/test_recovery.py

guidance-test:
	bash skills/ginflow/scripts/test-guidance.sh

## Check ginflow docs layout and artifact content guidance
artifact-guidance-test:
	python3 skills/ginflow/scripts/test-artifact-guidance.py

## Check ginflow Kanban gate and external harness statuses
kanban-harness-test:
	python3 skills/ginflow/scripts/test-kanban-harness.py

## Run model-backed ginflow blank-project integration test
harness-test: artifact-guidance-test kanban-harness-test
	bash skills/ginflow/scripts/test-blank-project.sh
