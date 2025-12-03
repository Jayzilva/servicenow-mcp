# Phase 1 – Test Cases and Results

## Environment
- Instance: `https://dev282111.service-now.com`
- Auth: Basic (`SERVICENOW_USERNAME=admin`)
- Credentials loaded from `.env` (password not shown)
- Python: 3.8+

## Summary
- Total: 4
- Passed: 4
- Failed: 0
- Duration: ~10s (network-dependent)

## Test Cases

### TC-001 – Authentication and Connectivity
- Purpose: Verify basic auth and API reachability
- Command: `pytest -q -s phase1_sn_api/test_auth.py`
- Expected: One incident record retrieved successfully, prints success
- Actual:
  - Output: `✅ ServiceNow connection verified via basic auth`
  - Status: Pass

### TC-002 – Create Incident
- Purpose: Create a new incident with required fields
- Command: `pytest -q -s phase1_sn_api/test_create_incident.py`
- Expected: Response contains `sys_id` and `number`, prints identifiers
- Actual:
  - Output: `✅ Created incident: number=INC0010005 sys_id=e6b042315369b21028cf51a0a0490eb3`
  - Status: Pass

### TC-003 – Read Incidents (Query + Get)
- Purpose: Query recent incidents and fetch one by `sys_id`
- Command: `pytest -q -s phase1_sn_api/test_read_incident.py`
- Expected: List of incidents printed; retrieval matches selected `sys_id`
- Actual:
  - Output:
    - `✅ Queried incidents (showing up to 5):`
    - `  INC0010003 | Laptop won't connect to VPN | sys_id=03c9adf153a5b21028cf51a0a0490e0c`
    - `  INC0008001 | ATF:TEST2 | sys_id=0c5f3cece1b12010f877971dea0b1449`
    - `  INC0000015 | I can't launch my VPN client since the last software update | sys_id=46e2fee9a9fe19810049b49dee0daf58`
    - `  INC0000016 | Rain is leaking on main DNS Server | sys_id=46e3e949a9fe19810069b824ba2c761a`
    - `  INC0000017 | How do I create a sub-folder | sys_id=46e482d9a9fe198101d3e3f3e2a14459`
    - `✅ Retrieved incident: number=INC0010003 sys_id=03c9adf153a5b21028cf51a0a0490e0c`
  - Status: Pass

### TC-004 – Update Incident
- Purpose: Update urgency and add work notes; verify persistence
- Command: `pytest -q -s phase1_sn_api/test_update_incident.py`
- Expected: Urgency changes to `1`; retrieval confirms updated value
- Actual:
  - Output:
    - `ℹ️ Created test incident for update: number=INC0010006 sys_id=abb0423153369b21028cf51a0a0490eeb`
    - `✅ Updated incident: number=INC0010006 sys_id=abb042315369b21028cf51a0a0490eeb urgency=1`
    - `✅ Verified persistence: number=INC0010006 sys_id=abb042315369b21028cf51a0a0490eeb urgency=1`
  - Status: Pass

## Execution Log (Suite)
- Command: `pytest -q -s phase1_sn_api`
- Result: `4 passed in 9.88s`

## Notes
- Journaling fields (e.g., `work_notes`) may require specific ACLs to display fully on read.
- The incident numbers and IDs are instance-specific and will vary.

