from execution_batch import authorize_batch, canonical_digest, create_batch


def package():
    return {
        "workflow_version": 2,
        "initiative_key": "APP-42",
        "package_revision": "APP-42/pkg-1",
        "contract": {"key": "C", "state": "approved", "objective": "ship", "boundaries": ["core"], "exclusions": ["deploy"], "acceptance": ["works"], "verification": ["make test"], "approval": {"approver": "gin", "approved_at": "2026-10-09T00:00:00Z"}},
        "spec": {"state": "approved", "key": "S", "behavior": ["works"], "interfaces": ["API"], "rules": ["safe"], "edge_cases": ["empty"], "constraints": ["local"]},
        "units": [{"key": "U", "plan_key": "P", "owner": "worker", "objective": "ship core", "scope": ["core"], "exclusions": ["deploy"], "acceptance": ["works"], "workspace": "/repo/u", "dependencies": [], "verification": ["make test"], "change_group": "CORE", "risk": "low", "escalation": "stop on failure"}],
        "plans": [{"key": "P", "unit_key": "U", "state": "approved", "steps": ["code"], "verification": ["make test"]}],
        "baseline": {"commit": "base", "verification": {"command": "make test", "result": "passed"}},
    }


def test_digest_is_canonical_and_authorization_binds_inputs():
    p = package()
    first = canonical_digest(p)
    assert first == canonical_digest({key: p[key] for key in reversed(p)})
    result = authorize_batch(p, actor={"id": "gin", "profile": "operator", "claim": "execution:authorize"}, budget={"max_turns": 10}, stop_conditions=["verification failure"], workspaces=["/repo/u"], baseline_commit="base")
    assert result["schema"] == "execution_batch/v1"
    assert result["batch_key"] == "APP-42/run-1"
    assert result["package_digest"] == first
    assert result["immutable"] is True


def test_changed_package_and_incomplete_ticket_rejected():
    p = package()
    try:
        authorize_batch(p, actor={"id": "gin", "profile": "operator", "claim": "execution:authorize"}, budget={"max_turns": 10}, stop_conditions=["stop"], workspaces=["/repo/u"], baseline_commit="wrong")
    except ValueError as error:
        assert "baseline" in str(error)
    else:
        raise AssertionError("changed baseline authorized")
    p["units"][0].pop("change_group")
    try:
        authorize_batch(p, actor={"id": "gin", "profile": "operator", "claim": "execution:authorize"}, budget={"max_turns": 10}, stop_conditions=["stop"], workspaces=["/repo/u"], baseline_commit="base")
    except ValueError as error:
        assert "change_group" in str(error)
    else:
        raise AssertionError("incomplete Ticket authorized")


def test_create_batch_delegates_legacy_card_creator():
    calls = []
    result = create_batch(package(), actor={"id": "gin", "profile": "operator", "claim": "execution:authorize"}, budget={"max_turns": 10}, stop_conditions=["stop"], workspaces=["/repo/u"], baseline_commit="base", create_card=lambda args: calls.append(args) or {"id": str(len(calls))})
    assert result["cards"]["integration_card"]["id"] == "2"
    assert calls[0]["metadata"]["initiative_key"] == "APP-42"


if __name__ == "__main__":
    test_digest_is_canonical_and_authorization_binds_inputs()
    test_changed_package_and_incomplete_ticket_rejected()
    test_create_batch_delegates_legacy_card_creator()
    print("execution batch tests passed")
