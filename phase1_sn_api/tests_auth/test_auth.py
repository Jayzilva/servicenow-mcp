import sys

from phase1_sn_api.servicenow_client import ServiceNowClient


def test_auth_connection() -> None:
    client = ServiceNowClient.from_env()
    assert client.verify_connection() is True, "Failed to verify ServiceNow connection with provided credentials"
    print("✅ ServiceNow connection verified via basic auth")

