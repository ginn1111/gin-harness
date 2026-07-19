.PHONY: setup apply verify verify-strict verify-test doctor doctor-deps community-update clean lint test harness-test artifact-guidance-test kanban-harness-test

# === Pre-flight ===
doctor:
	@echo "=== Hermes ==="; command -v hermes && hermes --version || echo "MISSING"
	@echo "=== CodeGraph ==="; command -v codegraph && codegraph --version || echo "MISSING"
	@echo "=== Python ==="; python3 --version
	@echo "=== Git ==="; git --version
	@echo "=== PyYAML ==="; python3 -c "import yaml; print('ok')" 2>/dev/null || echo "MISSING (pip install pyyaml)"

doctor-deps:
	python3 -m pip install pyyaml

# === Setup ===
## Preview profile setup
setup:
	@test -n "$(PROFILES)" || (echo 'Usage: make setup PROFILES="profile-a profile-b"' >&2; exit 2)
	./scripts/setup.sh $(PROFILES)

## Apply integrations to existing Hermes-native profiles
apply:
	@test -n "$(PROFILES)" || (echo 'Usage: make apply PROFILES="profile-a profile-b"' >&2; exit 2)
	./scripts/setup.sh --apply $(PROFILES)

## Verify integrations in existing profiles
verify:
	@test -n "$(PROFILES)" || (echo 'Usage: make verify PROFILES="profile-a profile-b"' >&2; exit 2)
	./scripts/verify.sh $(PROFILES)

## Verify profiles and fail on canonical repo drift
verify-strict:
	@test -n "$(PROFILES)" || (echo 'Usage: make verify-strict PROFILES="profile-a profile-b"' >&2; exit 2)
	./scripts/verify.sh --strict $(PROFILES)

## Test verify default and strict drift behavior
verify-test:
	bash scripts/test-verify.sh

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
	python3 -m py_compile scripts/*.py
	bash -n skills/ginflow/scripts/*.sh
	python3 -m py_compile skills/ginflow/scripts/*.py
	@echo "lint ok"

## Run deterministic repository tests
test: lint artifact-guidance-test kanban-harness-test

## Check ginflow docs layout and artifact content guidance
artifact-guidance-test:
	python3 skills/ginflow/scripts/test-artifact-guidance.py

## Check ginflow Kanban gate and external harness statuses
kanban-harness-test:
	python3 skills/ginflow/scripts/test-kanban-harness.py

## Run model-backed ginflow blank-project integration test
harness-test: artifact-guidance-test kanban-harness-test
	bash skills/ginflow/scripts/test-blank-project.sh
