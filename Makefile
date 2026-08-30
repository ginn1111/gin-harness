.PHONY: setup apply install uninstall install-test verify verify-strict verify-test setup-test doctor doctor-deps community-update clean lint test lifecycle-test plugin-test trace-test

ACTIVE_PROFILE := $(shell hermes profile list 2>/dev/null | python3 -c 'import re,sys; m=re.search(r"^\s*[◆*]\s*([A-Za-z0-9._-]+)", sys.stdin.read(), re.M); print(m.group(1) if m else "")')
PROFILES ?= $(ACTIVE_PROFILE)

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
	./scripts/setup.sh $(PROFILES)

## Apply integrations to existing Hermes-native profiles
apply:
	./scripts/setup.sh --apply $(PROFILES)

## Install Ginflow skill and plugin into every Hermes profile
install:
	bash scripts/install.sh install

## Remove installer-owned Ginflow integrations
uninstall:
	bash scripts/install.sh uninstall

## Verify integrations in existing profiles via ginflow harness
verify:
	@test -n "$(PROFILES)" || (echo 'No active Hermes profile found; run `hermes profile use <name>` or pass PROFILES="<name>"' >&2; exit 2)
	python3 skills/ginflow/scripts/validate-harness.py --setup-repo . --json

## Verify profiles and fail on canonical repo drift via ginflow harness
verify-strict:
	@test -n "$(PROFILES)" || (echo 'No active Hermes profile found; run `hermes profile use <name>` or pass PROFILES="<name>"' >&2; exit 2)
	python3 skills/ginflow/scripts/validate-harness.py --setup-repo . --json

## Test verify default and strict drift behavior
verify-test:
	bash scripts/test-verify.sh

## Test active-profile default selection
setup-test:
	bash scripts/test-setup.sh

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
test: lint setup-test lifecycle-test plugin-test install-test

## Canonical ginflow flat-flow integration test (single command, per-step PASS/FAIL)
lifecycle-test:
	python3 skills/ginflow/scripts/test-ginflow-lifecycle.py

install-test:
	bash scripts/test-install.sh

plugin-test:
	python3 plugins/ginflow-gate/test_ginflow_gate.py
	python3 plugins/ginflow-gate/test_blocker_reporting.py
	python3 plugins/ginflow-gate/test_recovery_policy.py
	python3 plugins/ginflow-gate/test_recovery.py
	$(MAKE) trace-test

trace-test:
	python3 plugins/ginflow-trace/test_ginflow_trace.py
	python3 plugins/ginflow-trace/test_ginflow_trace_integration.py
