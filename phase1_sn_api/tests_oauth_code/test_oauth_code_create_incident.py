import os
import pytest

from phase1_sn_api.servicenow_client import ServiceNowClient


def test_oauth_code_create_incident(monkeypatch: pytest.MonkeyPatch) -> None:
    if not os.getenv("SERVICENOW_AUTH_CODE") or not os.getenv("SERVICENOW_REDIRECT_URI"):
        pytest.skip("SERVICENOW_AUTH_CODE and SERVICENOW_REDIRECT_URI required for authorization code flow")
    monkeypatch.setenv("SERVICENOW_AUTH_TYPE", "oauth_code")
    client = ServiceNowClient.from_env()

    incident = client.create_incident(
        short_description="OAuth-code-created incident",
        urgency="2",
        impact="2",
        description="Created using OAuth authorization code",
    )

    assert "sys_id" in incident, "Create incident response missing sys_id"
    assert "number" in incident, "Create incident response missing number"
    print(f"✅ [OAuth Code] Created incident: number={incident['number']} sys_id={incident['sys_id']}")

