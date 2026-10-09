.PHONY: setup apply install uninstall install-test verify verify-strict verify-test setup-test doctor doctor-deps community-update clean lint test lifecycle-test plugin-test trace-test c2c with-chatgpt-test

# === Pre-flight ===
doctor:
	@echo "=== CodeGraph ==="; command -v codegraph && codegraph --version || echo "MISSING"
	@echo "=== Python ==="; python3 --version
	@echo "=== Git ==="; git --version

doctor-deps:
	python3 -m pip install pyyaml

# === Setup ===
## Preview profile setup
setup:
	./scripts/setup.sh $(PROFILES)

## Apply integrations to existing Hermes-native profiles
apply:
	./scripts/setup.sh --apply $(PROFILES)

## Install Ginflow skill to ~/.agents/skills and with-chatgpt into Hermes profiles (all profiles unless PROFILES is set)
install:
	bash scripts/install.sh install $(PROFILES)

## Remove installer-owned Ginflow integrations
uninstall:
	bash scripts/install.sh uninstall

## Verify integrations in existing profiles via ginflow harness
verify:
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

# === c2c ===
## Run vendored c2c CLI; extra args via C2C_ARGS (e.g. `make c2c C2C_ARGS="doctor --json"`)
c2c:
	@node --import tsx ./plugins/with-chatgpt/c2c/src/cli/index.ts $(C2C_ARGS)

with-chatgpt-test:
	python3 plugins/with-chatgpt/test_plugin.py

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
test: lint setup-test lifecycle-test plugin-test install-test

## Canonical ginflow flat-flow integration test (single command, per-step PASS/FAIL)
lifecycle-test:
	python3 skills/ginflow/scripts/test-ginflow-lifecycle.py

install-test:
	bash scripts/test-install.sh

plugin-test:
	python3 plugins/with-chatgpt/test_plugin.py
	hermes plugins validate plugins/with-chatgpt
	python3 plugins/ginflow-gate/test_ginflow_gate.py
	python3 plugins/ginflow-gate/test_blocker_reporting.py
	python3 plugins/ginflow-gate/test_recovery_policy.py
	python3 plugins/ginflow-gate/test_recovery.py
	python3 plugins/ginflow-gate/test_native_review_transition.py
	$(MAKE) trace-test

trace-test:
	python3 plugins/ginflow-trace/test_ginflow_trace.py
	python3 plugins/ginflow-trace/test_ginflow_trace_integration.py
