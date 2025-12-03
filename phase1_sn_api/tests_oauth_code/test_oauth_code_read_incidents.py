import os
import pytest

from phase1_sn_api.servicenow_client import ServiceNowClient


def test_oauth_code_query_and_get(monkeypatch: pytest.MonkeyPatch) -> None:
    if not os.getenv("SERVICENOW_AUTH_CODE") or not os.getenv("SERVICENOW_REDIRECT_URI"):
        pytest.skip("SERVICENOW_AUTH_CODE and SERVICENOW_REDIRECT_URI required for authorization code flow")
    monkeypatch.setenv("SERVICENOW_AUTH_TYPE", "oauth_code")
    client = ServiceNowClient.from_env()

    recent = client.query_incidents({"active": "true"}, limit=5)
    assert isinstance(recent, list), "query_incidents should return a list"
    assert len(recent) >= 1, "No active incidents found to read"

    print("✅ [OAuth Code] Queried incidents (showing up to 5):")
    for inc in recent:
        print(f"  {inc.get('number')} | {inc.get('short_description')} | sys_id={inc.get('sys_id')}")

    first = recent[0]
    detailed = client.get_incident(first["sys_id"])
    assert detailed["sys_id"] == first["sys_id"], "get_incident returned a different record"
    print(f"✅ [OAuth Code] Retrieved incident: number={detailed.get('number')} sys_id={detailed.get('sys_id')}")

