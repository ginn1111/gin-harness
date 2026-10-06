"""Tests for minimal Ginflow v2 execution package seam."""
from execution_package import validate_package


PACKAGE = {
    "workflow_version": 2,
    "initiative_key": "INIT-1",
    "contract": {
        "key": "INIT-1-CONTRACT",
        "state": "approved",
        "approval": {"approver": "gin", "approved_at": "2026-10-06T06:00:00Z"},
    },
    "spec": {"key": "INIT-1-SPEC", "state": "approved"},
    "units": [{
        "key": "UNIT-1",
        "plan_key": "PLAN-1",
        "owner": "ginb",
        "scope": ["core/ginflow-core"],
        "acceptance": ["validates"],
        "workspace": "/repo/unit-1",
        "dependencies": [],
    }],
    "plans": [{"key": "PLAN-1", "unit_key": "UNIT-1", "state": "approved"}],
    "baseline": {
        "commit": "abc123",
        "verification": {"command": "make test", "result": "passed"},
    },
}


def test_minimal_package_is_valid():
    assert validate_package(PACKAGE) == {"valid": True, "errors": []}


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
