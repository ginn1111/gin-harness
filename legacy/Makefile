.PHONY: doctor doctor-deps setup lint verify discover dry-run-new apply-new dry-run-shared apply-shared

# === Pre-flight ===

## Check prerequisites and report gaps
doctor:
	./scripts/doctor.sh

## Install Python dependencies
doctor-deps:
	python3 -m pip install -r requirements.txt

# === Bootstrap (new machine) ===

## Full setup: dependencies → profiles → shared skills → register
setup: doctor-deps apply-new apply-shared verify

# === Profiles ===

## Create delivery targets (dry-run)
dry-run-new:
	./scripts/scaffold-new.sh

## Create delivery targets (apply)
apply-new:
	./scripts/scaffold-new.sh --apply

# === Shared skills ===

## Clone and register shared skills (dry-run)
dry-run-shared:
	./scripts/install-shared-skills.sh
	./scripts/register-shared-skills.py

## Clone and register shared skills (apply)
apply-shared:
	./scripts/install-shared-skills.sh --apply
	./scripts/register-shared-skills.py --apply

# === Verification ===

## Full verification of delivery profiles
verify:
	./scripts/verify.sh

## Read-only discovery of existing profiles
discover:
	./scripts/discover-migration.sh

# === Hygiene ===

## Shell + Python syntax checks
lint:
	bash -n scripts/*.sh scripts/lib/*.sh
	python3 -m py_compile scripts/register-shared-skills.py
	bash -n scripts/doctor.sh
