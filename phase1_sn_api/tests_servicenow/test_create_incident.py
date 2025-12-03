from phase1_sn_api.servicenow_client import ServiceNowClient


def test_create_incident() -> None:
    client = ServiceNowClient.from_env()

    incident = client.create_incident(
        short_description="Laptop won't connect to VPN",
        urgency="2",
        impact="2",
        description="User unable to access company network remotely",
    )

    assert "sys_id" in incident, "Create incident response missing sys_id"
    assert "number" in incident, "Create incident response missing number"

    print(f"✅ Created incident: number={incident['number']} sys_id={incident['sys_id']}")
