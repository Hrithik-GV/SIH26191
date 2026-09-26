try:
    import pytest
except ImportError:
    pytest = None

from datetime import datetime, timezone
from backend.app.services.event_broker import (
    event_broker,
    EVENT_NEW_ALERT,
    EVENT_HAZARD_UPDATED,
    EVENT_HABITATION_PRIORITY_CHANGED,
    EVENT_RELOCATION_SITE_UPDATED,
    EVENT_DASHBOARD_UPDATED,
)
from backend.app.services.disaster_update_orchestrator import DisasterUpdateOrchestrator


def test_event_broker_broadcast_and_history():
    """Verify event broadcasting, ring buffer history, and required disclaimer."""
    test_payload = {
        "hazard_type": "flash_flood",
        "severity": "CRITICAL",
        "water_level": 5.2,
    }
    event = event_broker.broadcast(
        event_type=EVENT_HAZARD_UPDATED,
        data=test_payload,
        headline="River water level danger threshold breached",
        severity="CRITICAL",
    )

    assert event["event_type"] == EVENT_HAZARD_UPDATED
    assert event["severity"] == "CRITICAL"
    assert "River water level danger threshold breached" in event["headline"]
    assert "Relocation actions require competent administrative authority validation" in event["disclaimer"]

    # Check ring buffer history
    recent = event_broker.get_recent_events(limit=5)
    assert len(recent) > 0
    assert recent[0]["id"] == event["id"]


def test_disaster_orchestrator_heavy_rainfall_scenario():
    """
    Verify the 6-step reactive pipeline for heavy rainfall:
    1. Store observation
    2. Identify affected regions
    3. Recalculate hazard scores
    4. Recalculate habitation priorities
    5. Identify suitable relocation sites
    6. Update dashboard
    """
    res = DisasterUpdateOrchestrator.trigger_live_scenario("heavy_rainfall", db=None)

    # Step 1: Observation stored
    assert res["observation_stored"] is True
    assert "stored_record_id" in res

    # Step 2: Affected geographic regions
    assert len(res["affected_regions"]) >= 2
    assert "Wayanad District" in res["affected_regions"]
    assert "Vythiri Taluk" in res["affected_regions"]

    # Step 3: Hazard scores recalculated
    assert len(res["hazards_updated"]) >= 1
    hazard = res["hazards_updated"][0]
    assert hazard["severity"] == "CRITICAL"
    assert hazard["risk_score"] >= 90.0

    # Step 4: Habitation priorities recalculated
    assert len(res["priority_changes"]) >= 1
    immediate = [p for p in res["priority_changes"] if p["priority"] == "IMMEDIATE"]
    assert len(immediate) >= 1

    # Step 5: Suitable relocation sites identified
    assert len(res["candidate_sites"]) >= 1
    site = res["candidate_sites"][0]
    assert site["available_capacity"] > 0
    assert "limiting_factor" in site

    # Step 6: Dashboard updated
    dash = res["dashboard_summary"]
    assert dash["total_habitations"] > 0
    assert dash["immediate_relocation_count"] >= 3

    # Check emitted events
    emitted_types = [e["event_type"] for e in res["events_emitted"]]
    assert EVENT_NEW_ALERT in emitted_types
    assert EVENT_HAZARD_UPDATED in emitted_types
    assert EVENT_HABITATION_PRIORITY_CHANGED in emitted_types
    assert EVENT_RELOCATION_SITE_UPDATED in emitted_types
    assert EVENT_DASHBOARD_UPDATED in emitted_types


def test_disaster_orchestrator_river_surge_scenario():
    """Verify river surge scenario trigger and priority shift notification."""
    res = DisasterUpdateOrchestrator.trigger_live_scenario("river_surge", db=None)
    assert res["observation_stored"] is True
    assert any("Chooralmala" in r for r in res["affected_regions"])

    # Verify notification headlines
    headlines = [e["headline"] for e in res["events_emitted"]]
    assert any("HIGH risk" in h or "immediate assessment" in h or "River" in h for h in headlines)


def test_disaster_orchestrator_compliance_no_automatic_relocation():
    """
    Strict compliance check:
    Verify that notifications and event payloads NEVER claim a relocation decision was automatically made.
    """
    res = DisasterUpdateOrchestrator.trigger_live_scenario("landslide_warning", db=None)

    for evt in res["events_emitted"]:
        # Verify disclaimer in every event
        assert "disclaimer" in evt
        assert "competent administrative authority validation" in evt["disclaimer"]

        # Ensure no misleading "relocation decided" or "forced evacuation ordered" text
        assert "relocation decided" not in evt["headline"].lower()
        assert "automatic relocation" not in evt["headline"].lower()


if __name__ == "__main__":
    test_event_broker_broadcast_and_history()
    print("✓ test_event_broker_broadcast_and_history passed")
    test_disaster_orchestrator_heavy_rainfall_scenario()
    print("✓ test_disaster_orchestrator_heavy_rainfall_scenario passed")
    test_disaster_orchestrator_river_surge_scenario()
    print("✓ test_disaster_orchestrator_river_surge_scenario passed")
    test_disaster_orchestrator_compliance_no_automatic_relocation()
    print("✓ test_disaster_orchestrator_compliance_no_automatic_relocation passed")
    print("ALL 4 LIVE DISASTER EVENT TESTS PASSED!")

