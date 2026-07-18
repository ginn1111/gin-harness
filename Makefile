.PHONY: setup verify doctor doctor-deps community-update harness-test

# === Pre-flight ===
doctor:
	@echo "=== Hermes ==="; command -v hermes && hermes --version || echo "MISSING"
	@echo "=== Python ==="; python3 --version
	@echo "=== Git ==="; git --version
	@echo "=== PyYAML ==="; python3 -c "import yaml; print('ok')" 2>/dev/null || echo "MISSING (pip install pyyaml)"

doctor-deps:
	python3 -m pip install pyyaml

# === Setup ===
## Bootstrap delivery profiles (dry-run first)
setup:
	./scripts/setup.sh

## Apply setup (creates/modifies profiles)
apply:
	./scripts/setup.sh --apply

## Verify profiles match repo
verify:
	./scripts/verify.sh

# === Community assets ===
## Clone/pull community skill repos
community-update:
	./scripts/community-setup.sh --apply

# === Hygiene ===
lint:
	bash -n scripts/*.sh
	bash -n skills/ginflow/scripts/*.sh
	python3 -m py_compile skills/ginflow/scripts/*.py
	@echo "lint ok"

## Run model-backed ginflow blank-project integration test
harness-test:
	bash skills/ginflow/scripts/test-blank-project.sh
