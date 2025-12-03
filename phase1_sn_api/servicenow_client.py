import logging
import os
import time
from typing import Any, Dict, List, Optional

import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv


logger = logging.getLogger(__name__)
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(_handler)
logger.setLevel(logging.INFO)


class ServiceNowAuthError(Exception):
    """Raised when authentication with ServiceNow fails."""


class ServiceNowAPIError(Exception):
    """Raised when ServiceNow API returns an error response."""


class ServiceNowClient:
    """
    A client for interacting with the ServiceNow Table API (incident table).

    Provides helper methods for creating, reading, querying, and updating incidents.
    """

    def __init__(
        self,
        instance_url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        auth_type: str = "basic",
        timeout: int = 30,
        verify: bool = True,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ) -> None:
        """
        Initialize the ServiceNow client.

        Args:
            instance_url: Base URL of the ServiceNow instance (e.g., https://devXXXXX.service-now.com).
            username: ServiceNow username.
            password: ServiceNow password.
            auth_type: Authentication type (currently supports "basic").
            timeout: Request timeout in seconds.
            verify: Whether to verify SSL certificates.
        """
        if not instance_url:
            raise ValueError("instance_url must be provided")

        self.base_url = instance_url.rstrip("/")
        self.username = username or ""
        self.password = password or ""
        self.auth_type = auth_type.lower()
        self.timeout = timeout
        self.verify = verify
        self.client_id = client_id or os.getenv("SERVICENOW_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("SERVICENOW_CLIENT_SECRET", "")
        self.redirect_uri = redirect_uri or os.getenv("SERVICENOW_REDIRECT_URI", "")
        self._token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._token_expiry: Optional[float] = None

        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

        logger.debug(
            "Initialized ServiceNowClient base_url=%s auth_type=%s timeout=%s verify=%s",
            self.base_url,
            self.auth_type,
            self.timeout,
            self.verify,
        )

    @classmethod
    def from_env(cls, env_path: Optional[str] = None) -> "ServiceNowClient":
        """
        Create a client using environment variables loaded from a .env file.

        Supports two variable naming schemes:
        - SN_INSTANCE, SN_USER, SN_PASSWORD
        - SERVICENOW_INSTANCE_URL, SERVICENOW_USERNAME, SERVICENOW_PASSWORD, SERVICENOW_AUTH_TYPE

        Args:
            env_path: Optional path to a .env file. If None, defaults are used.

        Returns:
            ServiceNowClient instance configured from environment variables.
        """
        if env_path:
            load_dotenv(env_path)
        else:
            load_dotenv()

        instance_url = (
            os.getenv("SN_INSTANCE")
            or os.getenv("SERVICENOW_INSTANCE_URL")
        )
        username = (
            os.getenv("SN_USER")
            or os.getenv("SERVICENOW_USERNAME")
        )
        password = (
            os.getenv("SN_PASSWORD")
            or os.getenv("SERVICENOW_PASSWORD")
        )
        auth_type = os.getenv("SERVICENOW_AUTH_TYPE", "basic")
        client_id = os.getenv("SERVICENOW_CLIENT_ID")
        client_secret = os.getenv("SERVICENOW_CLIENT_SECRET")
        redirect_uri = os.getenv("SERVICENOW_REDIRECT_URI")

        if not instance_url:
            raise ValueError("Environment variable SN_INSTANCE or SERVICENOW_INSTANCE_URL is required")
        if auth_type.lower() == "basic":
            if not username:
                raise ValueError("Environment variable SN_USER or SERVICENOW_USERNAME is required")
            if not password:
                raise ValueError("Environment variable SN_PASSWORD or SERVICENOW_PASSWORD is required")
            return cls(instance_url=instance_url, username=username, password=password, auth_type=auth_type)
        elif auth_type.lower() == "oauth":
            if not client_id or not client_secret:
                raise ValueError("Environment variables SERVICENOW_CLIENT_ID and SERVICENOW_CLIENT_SECRET are required for OAuth")
            return cls(instance_url=instance_url, auth_type=auth_type, client_id=client_id, client_secret=client_secret)
        elif auth_type.lower() == "oauth_code":
            if not client_id or not client_secret:
                raise ValueError("Environment variables SERVICENOW_CLIENT_ID and SERVICENOW_CLIENT_SECRET are required for OAuth")
            if not redirect_uri:
                raise ValueError("Environment variable SERVICENOW_REDIRECT_URI is required for authorization code flow")
            return cls(
                instance_url=instance_url,
                auth_type=auth_type,
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                username=username,
                password=password,
            )
        else:
            raise NotImplementedError(f"Unsupported auth_type: {auth_type}")

    def _auth(self) -> Optional[HTTPBasicAuth]:
        if self.auth_type == "basic":
            return HTTPBasicAuth(self.username, self.password)
        return None

    def _ensure_token(self) -> str:
        if self._token and self._token_expiry and time.time() < self._token_expiry:
            return self._token
        url = f"{self.base_url}/oauth_token.do"
        if self.auth_type == "oauth":
            payload: Dict[str, Any] = {"grant_type": "client_credentials"}
        elif self.auth_type == "oauth_code":
            if self._refresh_token:
                payload = {"grant_type": "refresh_token", "refresh_token": self._refresh_token}
            else:
                auth_code = os.getenv("SERVICENOW_AUTH_CODE")
                if not auth_code:
                    raise ServiceNowAuthError("SERVICENOW_AUTH_CODE is required for initial authorization code exchange")
                payload = {
                    "grant_type": "authorization_code",
                    "code": auth_code,
                    "redirect_uri": self.redirect_uri,
                }
        else:
            raise NotImplementedError(f"Unsupported auth_type: {self.auth_type}")
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        try:
            resp = self.session.post(
                url,
                data=payload,
                headers=headers,
                auth=HTTPBasicAuth(self.client_id, self.client_secret),
                timeout=self.timeout,
                verify=self.verify,
            )
            if resp.status_code in (401, 403) and self.auth_type == "oauth":
                # Fallback to password grant if allowed
                payload_pwd = {
                    "grant_type": "password",
                    "username": self.username,
                    "password": self.password,
                }
                resp = self.session.post(
                    url,
                    data=payload_pwd,
                    headers=headers,
                    auth=HTTPBasicAuth(self.client_id, self.client_secret),
                    timeout=self.timeout,
                    verify=self.verify,
                )
        except requests.RequestException as exc:
            logger.error("HTTP request error: %s", exc)
            raise ServiceNowAPIError(str(exc)) from exc

        if resp.status_code in (401, 403):
            logger.error("Authentication/Authorization failed: status=%s body=%s", resp.status_code, resp.text)
            raise ServiceNowAuthError(f"Auth failed: {resp.status_code} {resp.text}")
        if not resp.ok:
            logger.error("ServiceNow OAuth token error: status=%s body=%s", resp.status_code, resp.text)
            raise ServiceNowAPIError(f"OAuth token error: {resp.status_code} {resp.text}")
        try:
            data = resp.json()
        except ValueError:
            logger.error("Invalid JSON response: %s", resp.text)
            raise ServiceNowAPIError("Invalid JSON response")
        token = data.get("access_token") or data.get("result", {}).get("access_token")
        if not token:
            raise ServiceNowAPIError("No access_token in OAuth response")
        expires_in = int(data.get("expires_in", 3600))
        refresh = data.get("refresh_token") or data.get("result", {}).get("refresh_token")
        self._token = token
        self._refresh_token = refresh
        self._token_expiry = time.time() + max(60, expires_in - 30)
        return token

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Internal HTTP request wrapper with error handling.

        Args:
            method: HTTP method (GET, POST, PATCH).
            path: API path starting with '/api/'.
            params: Query parameters.
            json: JSON body.

        Returns:
            Parsed JSON 'result' from ServiceNow responses.
        """
        url = f"{self.base_url}{path}"
        logger.debug("Request %s %s params=%s json=%s", method, url, params, json)

        try:
            headers = None
            auth = None
            if self.auth_type == "basic":
                auth = self._auth()
            elif self.auth_type in ("oauth", "oauth_code"):
                token = self._ensure_token()
                headers = {"Authorization": f"Bearer {token}"}
            resp = self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                json=json,
                auth=auth,
                headers=headers,
                timeout=self.timeout,
                verify=self.verify,
            )
        except requests.RequestException as exc:
            logger.error("HTTP request error: %s", exc)
            raise ServiceNowAPIError(str(exc)) from exc

        if resp.status_code in (401, 403):
            logger.error("Authentication/Authorization failed: status=%s body=%s", resp.status_code, resp.text)
            raise ServiceNowAuthError(f"Auth failed: {resp.status_code} {resp.text}")

        if not resp.ok:
            logger.error("ServiceNow API error: status=%s body=%s", resp.status_code, resp.text)
            raise ServiceNowAPIError(f"API error: {resp.status_code} {resp.text}")

        try:
            data = resp.json()
        except ValueError:
            logger.error("Invalid JSON response: %s", resp.text)
            raise ServiceNowAPIError("Invalid JSON response")

        result = data.get("result", data)
        logger.debug("Response result: %s", result)
        return result

    def verify_connection(self) -> bool:
        """
        Verify connectivity and credentials by querying the incident table with a small limit.

        Returns:
            True if the request succeeds, otherwise raises an error.
        """
        params = {"sysparm_limit": 1}
        _ = self._request("GET", "/api/now/table/incident", params=params)
        return True

    def create_incident(
        self,
        short_description: str,
        urgency: str,
        impact: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Create a new incident in ServiceNow.

        Args:
            short_description: Brief description of the incident.
            urgency: Urgency value (1=High, 2=Medium, 3=Low).
            impact: Impact value (1=High, 2=Medium, 3=Low).
            **kwargs: Additional fields to include (e.g., description, assignment_group).

        Returns:
            The created incident record.
        """
        payload: Dict[str, Any] = {
            "short_description": short_description,
            "urgency": str(urgency),
            "impact": str(impact),
        }
        payload.update(kwargs)
        return self._request("POST", "/api/now/table/incident", json=payload)

    def get_incident(self, sys_id: str) -> Dict[str, Any]:
        """
        Retrieve an incident by sys_id.

        Args:
            sys_id: The unique ID of the incident record.

        Returns:
            The incident record.
        """
        path = f"/api/now/table/incident/{sys_id}"
        return self._request("GET", path)

    def query_incidents(
        self,
        query_dict: Dict[str, Any],
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Query incidents using key/value filters.

        Args:
            query_dict: Dictionary of field filters (e.g., {"state": "1", "urgency": "2"}).
            limit: Maximum number of records to return.

        Returns:
            A list of incident records.
        """
        # Convert dict to sysparm_query format: key=value^key2=value2
        parts: List[str] = []
        for k, v in query_dict.items():
            parts.append(f"{k}={v}")
        sysparm_query = "^".join(parts)

        params = {
            "sysparm_query": sysparm_query,
            "sysparm_limit": int(limit),
        }
        result = self._request("GET", "/api/now/table/incident", params=params)
        # ServiceNow returns either a list or a dict depending on endpoint; ensure list
        return list(result) if isinstance(result, list) else [result]

    def update_incident(self, sys_id: str, updates_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update fields on an existing incident.

        Args:
            sys_id: The unique ID of the incident to update.
            updates_dict: Dictionary of fields to update (e.g., {"urgency": "1", "work_notes": "Investigating"}).

        Returns:
            The updated incident record.
        """
        path = f"/api/now/table/incident/{sys_id}"
        return self._request("PATCH", path, json=updates_dict)

