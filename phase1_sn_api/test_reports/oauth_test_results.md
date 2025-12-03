# Phase 1 – OAuth Test Cases and Results

## Environment
- Instance: `https://dev282111.service-now.com`
- Auth: OAuth client credentials via `.env`
- Client ID: present
- Client Secret: present
- Python: 3.8+
- Client: `phase1_sn_api/servicenow_client.py` with OAuth support

## Summary
- Total: 3
- Passed: 0
- Failed: 3
- Duration: ~6s (network-dependent)

## Test Cases

### TC-O01 – OAuth Connection
- Purpose: Verify token retrieval and table access via OAuth
- Source: `phase1_sn_api/tests_oauth/test_oauth_auth.py`
- Command: `pytest -q -s phase1_sn_api/tests_oauth/test_oauth_auth.py`
- Expected: Connection verified
- Actual:
  - Error: `ServiceNowAuthError: Auth failed: 401 {"error_description":"access_denied","error":"server_error"}`
  - Status: Fail

### TC-O02 – OAuth Create Incident
- Purpose: Create an incident using Bearer token
- Source: `phase1_sn_api/tests_oauth/test_oauth_create_incident.py`
- Command: `pytest -q -s phase1_sn_api/tests_oauth/test_oauth_create_incident.py`
- Expected: Incident created and identifiers printed
- Actual:
  - Error: `ServiceNowAuthError` during token retrieval (401 access_denied)
  - Status: Fail

### TC-O03 – OAuth Read Incidents
- Purpose: Query recent incidents and fetch one by `sys_id`
- Source: `phase1_sn_api/tests_oauth/test_oauth_read_incidents.py`
- Command: `pytest -q -s phase1_sn_api/tests_oauth/test_oauth_read_incidents.py`
- Expected: List printed and record retrieved
- Actual:
  - Error: `ServiceNowAuthError` during token retrieval (401 access_denied)
  - Status: Fail

## Observations
- Token endpoint called: `/<instance>/oauth_token.do`
- Grant used: `client_credentials` with Basic auth header (`client_id:client_secret`)
- Fallback attempted: `password` grant using `.env` username/password
- Both flows received `401 access_denied` from the instance

## Likely Causes in ServiceNow
- OAuth application registry not configured to allow `client_credentials` grant
- Client not active or misconfigured (ID/secret mismatch)
- Required scopes not defined or not permitted for the client
- Password grant disabled for the OAuth application (if fallback desired)

## Recommended Fixes
- In Application Registry:
  - Ensure the OAuth API endpoint is created for external clients and active
  - Enable `Client Credentials` grant for the application
  - Optional: enable `Resource Owner Password` grant if password fallback is desired
  - If scopes are required, define and allow them (e.g., `sn_api`)
- Confirm token endpoint: `https://<instance>/oauth_token.do`
- Verify the `.env` values match exactly the registry entry and are not expired or rotated

## Re-run After Fix
- Suite: `pytest -q -s phase1_sn_api/tests_oauth`
- Expected: All pass; incidents created and listed using Bearer tokens

