from decision import build_notification, build_projection, decision_ready


def evidence(**changes):
    value = {"id": "ev-1", "kind": "verification", "producer": "pytest", "commit": "result", "source": "make test", "result": "passed", "timestamp": "2026-10-09T12:00:00Z", "digest": "abc"}
    value.update(changes)
    return value


def base(**changes):
    value = {"initiative_key": "APP-42", "batch_key": "APP-42/run-1", "review_key": "APP-42/review-1", "baseline_commit": "base", "result_commit": "result", "target_commit": "target", "result_clean": True, "tickets": [{"key": "U", "state": "completed", "change_group": "CORE", "acceptance": ["A"], "paths": ["core/a.py"]}], "changed_paths": [{"path": "core/a.py", "change_group": "CORE"}], "evidence": [evidence()], "verification": {"commit": "result", "result": "passed"}, "findings": [], "claims": [{"text": "tests pass", "evidence_ids": ["ev-1"]}]}
    value.update(changes)
    return value


def test_successful_integration_opens_redacted_decision():
    assert decision_ready(base())["outcome"] == "decision_ready"
    projection = build_projection(base(), summary="safe summary")
    assert projection["schema"] == "decision_projection/v1"
    assert projection["behavior_delta"][0]["path"] == "core/a.py"
    assert "raw_log" not in projection


def test_readiness_rejects_running_or_unassigned_paths():
    for changes, expected in [({"tickets": [{"key": "U", "state": "running", "change_group": "CORE", "acceptance": [], "paths": []}]}, "running"), ({"changed_paths": [{"path": "x", "change_group": None}]}, "unassigned")]:
        try:
            decision_ready(base(**changes))
        except ValueError as error:
            assert expected in str(error)
        else:
            raise AssertionError("unsafe decision accepted")


def test_notification_has_idempotency_and_delivery_state():
    notification = build_notification(base(), message="review ready")
    assert notification["schema"] == "notification/v1"
    assert notification["idempotency_key"] == "APP-42/run-1:APP-42/review-1:decision_ready"
    assert notification["delivery"] == {"attempts": 0, "acknowledged": False, "replay_key": notification["idempotency_key"]}


if __name__ == "__main__":
    test_successful_integration_opens_redacted_decision()
    test_readiness_rejects_running_or_unassigned_paths()
    test_notification_has_idempotency_and_delivery_state()
    print("decision tests passed")
