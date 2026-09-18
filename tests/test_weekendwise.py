from trip_planner.graph import plan_weekend


def test_demo_replans_and_passes():
    result = plan_weekend("Vizag", "2026-09-19", "2026-09-20", 4, 10000)
    assert result["final_plan"]["status"] == "PASS"
    assert result["replan_count"] == 1
    assert result["final_plan"]["validation"] == {"status": "PASS", "issues": [], "recommendations": []}
    assert any(item["status"] == "warning" for item in result["execution_trace"])
    assert any(item["agent"] == "Validator" and item["status"] == "failed" for item in result["execution_trace"])


def test_max_replans_terminates():
    result = plan_weekend("Vizag", "2026-09-19", "2026-09-20", 4, 1, max_replans=0)
    assert result["replan_count"] == 0
    assert result["final_plan"]["status"] == "FAIL"
    assert result["final_plan"]["validation"]["issues"]


def test_weekend_length_is_bounded():
    try:
        plan_weekend("Vizag", "2026-09-19", "2026-09-22")
    except ValueError as exc:
        assert "1 to 3 days" in str(exc)
    else:
        raise AssertionError("Expected a 4-day request to be rejected")
