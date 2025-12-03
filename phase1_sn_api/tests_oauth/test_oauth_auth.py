import pytest

from phase1_sn_api.servicenow_client import ServiceNowClient


def test_oauth_connection(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SERVICENOW_AUTH_TYPE", "oauth")
    client = ServiceNowClient.from_env()
    assert client.verify_connection() is True, "OAuth connection verification failed"
    print("✅ ServiceNow connection verified via OAuth client credentials")

