# Phase 1 – Auth-Focused Test Cases and Results

## Environment
- Instance: `https://dev282111.service-now.com`
- Auth: Basic via `.env` (username/password)
- Python: 3.8+
- Client: `phase1_sn_api/servicenow_client.py`

## Summary
- Total: 4
- Passed: 4
- Failed: 0
- Duration: ~4s (network-dependent)

## Test Cases

### TC-A01 – Missing Environment Variables
- Purpose: Ensure client fails fast when required env vars are absent
- Source: `phase1_sn_api/test_auth_focus.py:12`
- Command: `pytest -q -s phase1_sn_api/test_auth_focus.py::test_from_env_missing_vars_raises`
- Expected: `ValueError`
- Actual: Pass (raises `ValueError`)

### TC-A02 – Unsupported Authentication Type
- Purpose: Reject unsupported `SERVICENOW_AUTH_TYPE`
- Source: `phase1_sn_api/test_auth_focus.py:27`
- Command: `pytest -q -s phase1_sn_api/test_auth_focus.py::test_unsupported_auth_type_raises`
- Expected: `NotImplementedError`
- Actual: Pass (raises `NotImplementedError` during `verify_connection()`)

### TC-A03 – Invalid Credentials
- Purpose: Fail authentication with wrong password
- Source: `phase1_sn_api/test_auth_focus.py:35`
- Command: `pytest -q -s phase1_sn_api/test_auth_focus.py::test_invalid_credentials_raise_auth_error`
- Expected: `ServiceNowAuthError`
- Actual:
  - Log: `Authentication/Authorization failed: status=401 ...`
  - Result: Pass (raises `ServiceNowAuthError`)

### TC-A04 – Nonexistent Record
- Purpose: Error when fetching a record that does not exist
- Source: `phase1_sn_api/test_auth_focus.py:44`
- Command: `pytest -q -s phase1_sn_api/test_auth_focus.py::test_nonexistent_record_raises_api_error`
- Expected: `ServiceNowAPIError`
- Actual:
  - Log: `ServiceNow API error: status=404 ...`
  - Result: Pass (raises `ServiceNowAPIError`)

## Suite Execution
- Command: `pytest -q -s phase1_sn_api/test_auth_focus.py`
- Result: `4 passed in 3.69s`

## Notes
- Env handling is strict: missing `SN_*` or `SERVICENOW_*` variables cause a `ValueError` on initialization
- Only `basic` auth is supported in Phase 1; other types are intentionally rejected
- Error pathways map cleanly to exceptions for reliable upstream handling

