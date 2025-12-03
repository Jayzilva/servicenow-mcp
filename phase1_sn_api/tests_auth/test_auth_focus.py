import os
import pytest
from pathlib import Path

from phase1_sn_api.servicenow_client import (
    ServiceNowClient,
    ServiceNowAuthError,
    ServiceNowAPIError,
)


def test_from_env_missing_vars_raises(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("SN_INSTANCE", raising=False)
    monkeypatch.delenv("SN_USER", raising=False)
    monkeypatch.delenv("SN_PASSWORD", raising=False)
    monkeypatch.delenv("SERVICENOW_INSTANCE_URL", raising=False)
    monkeypatch.delenv("SERVICENOW_USERNAME", raising=False)
    monkeypatch.delenv("SERVICENOW_PASSWORD", raising=False)

    empty_env = tmp_path / "empty.env"
    empty_env.write_text("")

    with pytest.raises(ValueError):
        ServiceNowClient.from_env(env_path=str(empty_env))


def test_unsupported_auth_type_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SERVICENOW_AUTH_TYPE", "oauth")

    client = ServiceNowClient.from_env()
    with pytest.raises(NotImplementedError):
        client.verify_connection()


def test_invalid_credentials_raise_auth_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SERVICENOW_PASSWORD", "wrong_password")
    monkeypatch.setenv("SERVICENOW_AUTH_TYPE", "basic")

    client = ServiceNowClient.from_env()
    with pytest.raises(ServiceNowAuthError):
        client.verify_connection()


def test_nonexistent_record_raises_api_error() -> None:
    client = ServiceNowClient.from_env()
    with pytest.raises(ServiceNowAPIError):
        client.get_incident("invalid_sys_id")
