import os
import pytest

from phase1_sn_api.servicenow_client import ServiceNowClient


def test_oauth_code_connection(monkeypatch: pytest.MonkeyPatch) -> None:
    if not os.getenv("SERVICENOW_AUTH_CODE") or not os.getenv("SERVICENOW_REDIRECT_URI"):
        pytest.skip("SERVICENOW_AUTH_CODE and SERVICENOW_REDIRECT_URI required for authorization code flow")
    monkeypatch.setenv("SERVICENOW_AUTH_TYPE", "oauth_code")
    client = ServiceNowClient.from_env()
    assert client.verify_connection() is True, "OAuth code connection verification failed"
    print("✅ ServiceNow connection verified via OAuth authorization code")

