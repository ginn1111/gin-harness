"""Tests for minimal Ginflow v2 execution package seam."""
from execution_package import approve_package, shape_package, validate_package


PACKAGE = {
    "workflow_version": 2,
    "initiative_key": "INIT-1",
    "contract": {
        "key": "INIT-1-CONTRACT",
        "state": "approved",
        "objective": "ship",
        "boundaries": ["core"],
        "exclusions": ["deploy"],
        "acceptance": ["passes"],
        "verification": ["make test"],
        "approval": {"approver": "gin", "approved_at": "2026-10-06T06:00:00Z"},
    },
    "spec": {
        "key": "INIT-1-SPEC", "state": "approved", "behavior": ["works"],
        "interfaces": ["API"], "rules": ["safe"], "edge_cases": ["empty"], "constraints": ["local"],
    },
    "units": [{
        "key": "UNIT-1",
        "plan_key": "PLAN-1",
        "owner": "ginb",
        "scope": ["core/ginflow-core"],
        "acceptance": ["validates"],
        "workspace": "/repo/unit-1",
        "dependencies": [],
    }],
    "plans": [{"key": "PLAN-1", "unit_key": "UNIT-1", "state": "approved", "steps": ["code"], "verification": ["make test"]}],
    "baseline": {
        "commit": "abc123",
        "verification": {"command": "make test", "result": "passed"},
    },
}


def test_minimal_package_is_valid():
    assert validate_package(PACKAGE) == {"valid": True, "errors": []}


def test_shaping_and_approval_are_single_package_operations():
    draft = shape_package(
        "INIT-2",
        {"key": "INIT-2-CONTRACT", "objective": "ship", "boundaries": ["core"], "exclusions": ["deploy"], "acceptance": ["passes"], "verification": ["make test"]},
        {"key": "INIT-2-SPEC", "behavior": ["works"], "interfaces": ["API"], "rules": ["safe"], "edge_cases": ["empty"], "constraints": ["local"]},
        PACKAGE["units"],
        [{"key": "PLAN-1", "unit_key": "UNIT-1", "steps": ["code"], "verification": ["make test"]}],
        PACKAGE["baseline"],
    )
    assert draft["contract"]["state"] == "draft"
    approved = approve_package(draft, "gin", "2026-10-06T06:00:00Z")
    assert validate_package(approved)["valid"] is True
    assert approved["contract"]["approval"]["approver"] == "gin"


def test_incomplete_package_cannot_be_approved():
    draft = shape_package("INIT-3", {}, {}, [], [], {})
    try:
        approve_package(draft, "gin", "2026-10-06T06:00:00Z")
    except ValueError as error:
        assert "incomplete execution package" in str(error)
    else:
        raise AssertionError("incomplete package approved")


def test_package_rejects_cycle_deterministically():
    package = {**PACKAGE, "units": [
        {**PACKAGE["units"][0], "dependencies": ["UNIT-2"]},
        {**PACKAGE["units"][0], "key": "UNIT-2", "plan_key": "PLAN-2", "dependencies": ["UNIT-1"]},
    ], "plans": [
        PACKAGE["plans"][0], {"key": "PLAN-2", "unit_key": "UNIT-2", "state": "approved"},
    ]}
    result = validate_package(package)
    assert result["valid"] is False
    assert "unit dependencies must be acyclic" in result["errors"]


if __name__ == "__main__":
    test_minimal_package_is_valid()
    test_package_rejects_cycle_deterministically()
    print("execution package tests passed")
