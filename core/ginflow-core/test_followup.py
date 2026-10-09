from followup import route_followup


def test_bounded_correction_creates_new_batch_packet():
    packet = route_followup({"delta_class": "implementation", "initiative_key": "APP-42", "review_key": "APP-42/review-1", "delta": "fix typo", "scope": ["core/a.py"], "exclusions": ["deploy"], "acceptance": ["test passes"], "verification": ["make test"], "risk": "low", "ticket_mapping": ["U"]})
    assert packet["route"] == "Execution"
    assert packet["packet"]["batch_attempt"] == 2
    assert packet["policy_proposals"] == []


def test_contract_and_foundation_changes_route_upward():
    assert route_followup({"delta_class": "contract", "initiative_key": "APP-42", "review_key": "R", "delta": "new API", "scope": ["api"], "exclusions": [], "acceptance": ["works"], "verification": ["test"], "risk": "medium", "ticket_mapping": ["U"]})["route"] == "Shaping"
    assert route_followup({"delta_class": "problem", "initiative_key": "APP-42", "review_key": "R", "delta": "new goal", "scope": ["all"], "exclusions": [], "acceptance": ["aligned"], "verification": ["review"], "risk": "high", "ticket_mapping": []})["route"] == "Discovery"


def test_followup_rejects_string_collections():
    request = {"delta_class": "implementation", "initiative_key": "APP-42", "review_key": "R", "delta": "fix", "scope": "core/a.py", "exclusions": [], "acceptance": ["works"], "verification": ["test"], "risk": "low", "ticket_mapping": ["U"]}
    try:
        route_followup(request)
    except ValueError as error:
        assert "scope" in str(error)
    else:
        raise AssertionError("string scope accepted")


if __name__ == "__main__":
    test_bounded_correction_creates_new_batch_packet()
    test_contract_and_foundation_changes_route_upward()
    test_followup_rejects_string_collections()
    print("follow-up tests passed")
