# ServiceNow LLM Integration POC – Phase 1

## Overview
This Phase 1 implements a production-quality Python client for the ServiceNow Table API and four focused tests to validate basic auth, incident creation, reading, and updating. It is designed to be used standalone and later extended by the MCP server.

## Prerequisites
- Python 3.8+
- Access to a ServiceNow instance with API access (PDI is fine)
- A user account with rights to create/update incidents

## Configuration
1. Copy `.env.example` to `.env` and set credentials.
2. Either naming scheme works (the client supports both):
   - SN_INSTANCE, SN_USER, SN_PASSWORD
   - SERVICENOW_INSTANCE_URL, SERVICENOW_USERNAME, SERVICENOW_PASSWORD, SERVICENOW_AUTH_TYPE

Example using `SERVICENOW_*` variables:
```
SERVICENOW_INSTANCE_URL=https://devXXXXX.service-now.com
SERVICENOW_USERNAME=admin
SERVICENOW_PASSWORD=your_password_here
SERVICENOW_AUTH_TYPE=basic
```

## Setup
```
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Running Tests
Each test runs independently. Use `-s` to show prints; `-q` for concise output.

- Auth check:
```
pytest -q -s phase1_sn_api/test_auth.py
```
Expected success sample:
```
✅ ServiceNow connection verified via basic auth
1 passed in 2.10s
```

- Create incident:
```
pytest -q -s phase1_sn_api/test_create_incident.py
```
Expected success sample:
```
✅ Created incident: number=INC0012345 sys_id=8b1f...abcd
1 passed in 1.75s
```

- Read incidents:
```
pytest -q -s phase1_sn_api/test_read_incident.py
```
Expected success sample:
```
✅ Queried incidents (showing up to 5):
  INC0012345 | Laptop won't connect to VPN | sys_id=8b1f...abcd
  INC0012346 | ...
✅ Retrieved incident: number=INC0012345 sys_id=8b1f...abcd
1 passed in 1.90s
```

- Update incident:
```
pytest -q -s phase1_sn_api/test_update_incident.py
```
Expected success sample:
```
ℹ️ Created test incident for update: number=INC0012347 sys_id=2c9e...ef01
✅ Updated incident: number=INC0012347 sys_id=2c9e...ef01 urgency=1
✅ Verified persistence: number=INC0012347 sys_id=2c9e...ef01 urgency=1
1 passed in 2.40s
```

## Notes on ServiceNow API
- Table API base path: `/api/now/table/incident`
- Create: `POST /api/now/table/incident`
- Read single: `GET /api/now/table/incident/{sys_id}`
- Query list: `GET /api/now/table/incident?sysparm_query=...&sysparm_limit=...`
- Update: `PATCH /api/now/table/incident/{sys_id}`

## What Success Looks Like
- All four tests pass
- Prints show incident numbers and sys_ids
- Your ServiceNow UI shows the created records

## Troubleshooting
- 401/403 errors usually indicate wrong credentials or insufficient roles
- Ensure the user has permission to use the Table API and the incident table
- If journaling fields like `work_notes` do not appear in reads, verify ACLs and field-level access; urgency update is still validated

## Next Steps
After Phase 1 passes, proceed to Phase 2 (MCP server) per `poc.md`.

