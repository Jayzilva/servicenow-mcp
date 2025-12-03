✅ ARCHITECTURE DOCUMENT – INTRODUCTION & USE CASE IMPLEMENTATION
(LLM Bot + MCP Server + ServiceNow + SSO Token Exchange Architecture)
1. General Introduction
1.1 Purpose of This Document
This document defines the architectural approach for enabling secure, user-authenticated interactions between a Large Language Model (LLM) bot, an MCP (Model Context Protocol) middleware server, and the ServiceNow platform. The intention is to ensure:
A consistent identity model across all systems
Compliance with enterprise Single Sign-On (SSO) requirements
Secure delegation of user authority from the bot to downstream APIs
Elimination of service accounts, passwords, or shared credentials
Maintainability and long-term extensibility
This document provides both a conceptual overview and practical implementation guidance for the development team.
1.2 High-Level Architectural Problem
A user interacts with an LLM bot. The bot must perform operations in ServiceNow as that user, respecting the user's permissions, access controls, and audit trails. However:
The bot cannot hold user credentials
The user cannot interactively authenticate during each bot request
ServiceNow must recognize the real user, not a generic service identity
The system must meet enterprise SSO security standards
The solution is a token delegation model using OAuth 2.0 Token Exchange (On-Behalf-Of Flow) where the MCP server exchanges the user’s identity token for a ServiceNow-specific access token.
1.3 Identity & Protocol Foundation
This architecture is based on industry-standard authentication protocols:
OpenID Connect (OIDC)
Used to authenticate users and obtain identity-related tokens.
OAuth 2.0
Used for authorization and delegated API access across services.
Key OAuth flows used here:
Authorization Code Flow (for initial user authentication)
OAuth 2.0 Token Exchange / On-Behalf-Of (OBO) Flow
Backend confidential client authentication (client secret or certificate)
Single Sign-On (SSO)
All components rely on a centralized Identity Provider (IdP), such as:
Azure AD / Entra ID
Okta
Ping Identity
Keycloak
ADFS
Using the same IdP is crucial because it allows seamless user identity propagation across APIs.
1.4 Core Architectural Principles
1.4.1 User Identity Flows End-to-End
The user authenticates once using SSO.
Their identity flows across all layers without reauthentication.
1.4.2 No Service Accounts
The system avoids shared secrets and impersonation using built-in ServiceNow impersonation APIs.
Instead, real user identities and ACLs are used.
1.4.3 Zero Trust / Least Privilege
Each access token is:
short-lived
scoped
audience-restricted
refreshed via the IdP only when required
1.4.4 Auditability
ServiceNow logs reflect the real human actor, not the middleware.
2. Specific Use Case Implementation
This section describes exactly how we will implement the architecture for:
User → LLM Bot → MCP Server → ServiceNow
All components use the same SSO provider.
2.1 Components
2.1.1 LLM Bot (Client)
Acts as the user-facing system.
Responsible for:
Obtaining the user identity token from the chat platform’s SSO
Passing the token to the MCP server
Not storing or handling ServiceNow tokens
2.1.2 MCP Server (Middleware / API #1)
A secure backend service responsible for:
Validating user tokens
Performing OAuth 2.0 Token Exchange (OBO)
Managing per-user ServiceNow access tokens
Making authenticated REST API calls to ServiceNow
Enforcing business logic and API orchestration
This server is a confidential OAuth client and performs server-side secure operations.
2.1.3 ServiceNow (API #2)
Configured to trust the same IdP.
ServiceNow receives:
The exchanged access token containing the user’s identity
Applies ACLs and roles based on that identity
Processes API requests as the user
2.2 Authentication and Token Exchange Flow
Step 1 – User Authenticates via SSO
User logs into the company system (Teams, Slack, or custom UI).
The Identity Provider issues:
ID Token
Access Token (audience = MCP server)
Step 2 – LLM Bot → MCP Server
Bot forwards the user’s access token:
Authorization: Bearer <user token>
Step 3 – MCP Server Performs Token Exchange (OBO)
The MCP server sends a token exchange request to the IdP:
POST /oauth2/token
grant_type=urn:ietf:params:oauth:grant-type:token-exchange
subject_token=<user_access_token>
audience=servicenow
scope=sn_api
client_id=<mcp_client_id>
client_secret=<mcp_secret>
IdP returns:
access_token=<token usable by ServiceNow>
This token includes:
sub = real user’s ID
aud = ServiceNow
roles/scopes configured for ServiceNow API access
Step 4 – MCP Server Calls ServiceNow
API request:
Authorization: Bearer <servicenow_access_token>
ServiceNow validates the token and executes the action as the actual user.
Step 5 – ServiceNow Response → MCP → Bot → User
MCP returns structured data to the LLM bot.
2.3 Required Configuration by Platform
2.3.1 Identity Provider (Azure AD / Okta / Ping / Keycloak)
Register ServiceNow as an OAuth resource server
Register MCP Server as a confidential client
Enable Token Exchange / OBO flow
Configure scopes (sn_api, incident.read, etc.)
Define allowed audiences
2.3.2 MCP Server
Implement JWT validation
Implement token exchange logic
Maintain secure storage for client secrets
Provide an abstraction layer for ServiceNow APIs
Log actions with user identity
2.3.3 ServiceNow
Enable OAuth JWT bearer authentication (or external IdP authentication)
Configure OAuth provider in ServiceNow
Map external user identity claims to ServiceNow users
Confirm ACL behavior based on user identity
2.4 Sequence Diagram (Text Version)
User
  │ logs in via SSO
  ▼
LLM Bot
  │ passes user token
  ▼
MCP Server
  │ validate user
  │ exchange token (OBO)
  ▼
Identity Provider (SSO/IdP)
  │ issues SN token
  ▼
MCP Server
  │ call ServiceNow as user
  ▼
ServiceNow
  │ return data authorized for user
2.5 Benefits of This Architecture
✔ Single Sign-On across the entire workflow
✔ No user credentials in code
✔ MCP acts only as a secure identity delegator
✔ ServiceNow sees and enforces the real user’s ACLs
✔ Full audit trail – every SN action logs the actual human
✔ Scalable and reusable for future backend API integrations