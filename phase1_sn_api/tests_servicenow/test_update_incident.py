from phase1_sn_api.servicenow_client import ServiceNowClient


def test_update_incident() -> None:
    client = ServiceNowClient.from_env()

    created = client.create_incident(
        short_description="Test update incident",
        urgency="3",
        impact="3",
        description="Initial description",
    )

    sys_id = created["sys_id"]
    print(f"ℹ️ Created test incident for update: number={created['number']} sys_id={sys_id}")

    updated = client.update_incident(sys_id, {"urgency": "1", "work_notes": "Investigating issue"})
    assert updated["sys_id"] == sys_id, "Updated incident sys_id mismatch"
    assert str(updated.get("urgency")) == "1", "Urgency did not update to 1 (High)"

    print(
        f"✅ Updated incident: number={updated.get('number')} sys_id={sys_id} urgency={updated.get('urgency')}"
    )

    fetched = client.get_incident(sys_id)
    assert str(fetched.get("urgency")) == "1", "Urgency not persisted after update"
    print(f"✅ Verified persistence: number={fetched.get('number')} sys_id={sys_id} urgency={fetched.get('urgency')}")
