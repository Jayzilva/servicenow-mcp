import pytest

from phase1_sn_api.servicenow_client import ServiceNowClient


def test_oauth_create_incident(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SERVICENOW_AUTH_TYPE", "oauth")
    client = ServiceNowClient.from_env()

    incident = client.create_incident(
        short_description="OAuth-created incident",
        urgency="2",
        impact="2",
        description="Created using OAuth client credentials",
    )

    assert "sys_id" in incident, "Create incident response missing sys_id"
    assert "number" in incident, "Create incident response missing number"
    print(f"✅ [OAuth] Created incident: number={incident['number']} sys_id={incident['sys_id']}")

