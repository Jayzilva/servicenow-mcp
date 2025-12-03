# ServiceNow LLM Integration POC

## Context
I'm building a proof-of-concept that connects an LLM bot to ServiceNow through a secure MCP (Model Context Protocol) middleware server. The goal is to allow users to interact with ServiceNow via natural language while maintaining proper authentication and user identity.

## Architecture Overview
```
User → LLM Bot (Claude) → MCP Server (Python/FastAPI) → ServiceNow (PDI)
```

## Tech Stack
- **Backend**: Python 3.8+, FastAPI
- **LLM**: Anthropic Claude (claude-sonnet-4-20250514)
- **Target System**: ServiceNow Personal Developer Instance (PDI)
- **Auth (Phase 4)**: OAuth 2.0 Token Exchange, JWT

## Project Structure Needed
```
servicenow-llm-poc/
├── .env                          # Environment variables
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation
│
├── phase1_sn_api/               # Phase 1: ServiceNow API tests
│   ├── test_auth.py
│   ├── test_create_incident.py
│   ├── test_read_incident.py
│   ├── test_update_incident.py
│   └── servicenow_client.py     # SN API wrapper class
│
├── phase2_mcp_server/           # Phase 2: MCP Server
│   ├── mcp_server.py            # FastAPI application
│   ├── models.py                # Pydantic models
│   ├── config.py                # Configuration
│   └── test_mcp.py              # MCP tests
│
├── phase3_llm/                  # Phase 3: LLM Integration
│   ├── llm_client.py            # Claude integration
│   ├── tools.py                 # Tool definitions
│   ├── test_llm_tools.py
│   └── chat_example.py          # Example conversation
│
├── phase4_auth/                 # Phase 4: Authentication
│   ├── auth_middleware.py       # JWT validation
│   ├── token_exchange.py        # OAuth token exchange
│   └── test_auth_flow.py
│
└── phase5_integration/          # Phase 5: E2E tests
    ├── test_e2e.py
    └── test_permissions.py
```

## Implementation Request

### Current Phase: Phase 1 - ServiceNow API Foundation

Please help me implement **Phase 1** with the following requirements:

#### 1. Create `servicenow_client.py`
A clean, reusable Python class to interact with ServiceNow REST API:

**Requirements:**
- Use `requests` library
- Support Basic Authentication (username/password)
- Implement methods:
  - `create_incident(short_description, urgency, impact, **kwargs)`
  - `get_incident(sys_id)`
  - `query_incidents(query_dict, limit=10)`
  - `update_incident(sys_id, updates_dict)`
- Include proper error handling with custom exceptions
- Add logging for debugging
- Return parsed JSON responses
- Include docstrings for all methods

#### 2. Create Test Scripts
Individual test files that verify each operation:

**test_auth.py:**
- Test basic authentication
- Verify connection to ServiceNow
- Print success/failure clearly

**test_create_incident.py:**
- Create a sample incident
- Print incident number and sys_id
- Verify it appears in ServiceNow UI

**test_read_incident.py:**
- Query recent incidents
- Display incident details in readable format
- Test both get_incident() and query_incidents()

**test_update_incident.py:**
- Create an incident
- Update its urgency and add work notes
- Verify changes

#### 3. Configuration
**requirements.txt** with:
```
requests>=2.31.0
python-dotenv>=1.0.0
pytest>=7.4.0
```

**.env.example:**
```
SN_INSTANCE=https://devXXXXX.service-now.com
SN_USER=admin
SN_PASSWORD=your_password_here
```

#### 4. Documentation
**README.md** with:
- Quick start instructions
- How to set up .env file
- How to run each test
- What success looks like for each test

## Specific Guidelines

### Code Style
- Use type hints
- Follow PEP 8
- Include comments for complex logic
- Use f-strings for formatting
- Prefer explicit over implicit

### Error Handling
- Create custom exception classes (e.g., `ServiceNowAPIError`, `ServiceNowAuthError`)
- Catch and log HTTP errors
- Provide helpful error messages

### Testing
- Each test should be runnable independently
- Use clear assertions with messages
- Print progress and results
- Exit with proper status codes

### Security
- Never hardcode credentials
- Use environment variables
- Add .env to .gitignore
- Provide .env.example template

## Example Usage I Want to Achieve

```python
from servicenow_client import ServiceNowClient

# Initialize client
client = ServiceNowClient.from_env()

# Create incident
incident = client.create_incident(
    short_description="Laptop won't connect to VPN",
    urgency="2",
    impact="2",
    description="User unable to access company network remotely"
)

print(f"Created: {incident['number']}")

# Query incidents
recent = client.query_incidents(
    {"state": "1", "urgency": "2"},
    limit=5
)

for inc in recent:
    print(f"{inc['number']}: {inc['short_description']}")
```

## What I Need From You

1. **Generate the complete code** for Phase 1 files
2. **Explain how to run each test** step-by-step
3. **Show me what successful output looks like** for each test
4. **Point out any prerequisites** I need to configure in ServiceNow
5. **Suggest improvements** to make the code more robust

## Additional Context

- My ServiceNow PDI is fresh (default configuration)
- I'm comfortable with Python but new to ServiceNow APIs
- I want clean, production-quality code (even for POC)
- I'll be sharing this with my team, so documentation matters

## After Phase 1 Success

Once Phase 1 is complete and all tests pass, I'll ask you to help with:
- **Phase 2**: Building the FastAPI MCP server
- **Phase 3**: Integrating Claude as the LLM interface
- **Phase 4**: Adding OAuth and token exchange
- **Phase 5**: End-to-end integration testing

---

**Please start by implementing Phase 1 completely, with all files, tests, and documentation. Make it production-ready and easy to understand.**