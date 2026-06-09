from dataclasses import dataclass
from typing import Dict

import requests
import httpx
import os
from PureCloudPlatformClientV2 import ApiClient
from PureCloudPlatformClientV2.rest import ApiException
from fastapi import HTTPException
from app.core.exceptions import ConfigException, AppException
import httpx
from app.models.schemas import OrgCredentials
# from app.services.token_service import TokenService
from PureCloudPlatformClientV2 import ApiClient, RoutingApi ,OrganizationApi
from urllib.parse import urlparse
import time

# class GenesysClient:
#     """
#     API client with:
#     - bearer token from TokenService
#     - 401 refresh once and retry once
#     """

#     def __init__(self, token_service: TokenService,http_client: httpx.AsyncClient, timeout_seconds: int = 30):
#         self.token_service = token_service
#         self.timeout_seconds = timeout_seconds
#         self.http_client = http_client

    # async def get_org_me(self, org: OrgCredentials) -> httpx.Response:
    #     path = "/api/v2/organizations/me"
    #     return await self.request_with_retry(org, "GET", path)

    # async def request_with_retry(self, org: OrgCredentials, method: str, path: str, **kwargs) -> httpx.Response:
    #     url = f"{org.api_base_url}{path}"
    #     token = await self.token_service.get_token(org)
    #     headers = kwargs.pop("headers", {})
    #     headers["Authorization"] = f"Bearer {token}"

    #     async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
    #         resp = await client.request(method, url, headers=headers, **kwargs)

    #         if resp.status_code == 401:
    #             # Token expired/clock-skew/revoked => refresh once
    #             self.token_service.invalidate(org.org_name)
    #             new_token = await self.token_service.get_token(org, force_refresh=True)
    #             headers["Authorization"] = f"Bearer {new_token}"
    #             resp = await client.request(method, url, headers=headers, **kwargs)

    #         return resp


def api_base_to_login_endpoint(api_base_url: str) -> str:
    """
    Input:  https://api.mypurecloud.ie
    Output: login.mypurecloud.ie
    """
    # Step 1: remove extra spaces using strip 
    # Step 2: parse URL safely
    # urlparse helps separate scheme, host, path, query, etc.
    # Example: "https://api.mypurecloud.ie/some/path"
    #   scheme = https
    #   netloc = api.mypurecloud.ie
    parsed = urlparse(api_base_url.strip())
    # Step 3: get host
    # - If scheme exists, host is in parsed.netloc
    # - If no scheme (e.g., "api.mypurecloud.ie"), netloc is empty,
    #   then use parsed.path as fallback
    host = parsed.netloc or parsed.path  # handles with/without scheme
    host = host.strip("/").lower()
     # Step 4: if host starts with "api.", replace with "login."
    if host.startswith("api."):
        return "login." + host[len("api."):]
    
    # Step 5: if already login domain, return as-is
    # fallback: if already login.* or custom host
    if host.startswith("login."):
        return host

    # generic fallback (optional): prepend login.
    return f"login.{host}"

def get_client_credentials_token(
    api_base_url: str,   # e.g. login.mypurecloud.ie
    client_id: str,
    client_secret: str
) -> tuple[str, int]:
    
    login_endpoint=api_base_to_login_endpoint(api_base_url)
    token_url = f"https://{login_endpoint}/oauth/token"

    payload = {"grant_type": "client_credentials"}
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    resp = requests.post(
        token_url,
        data=payload,
        headers=headers,
        auth=(client_id.strip(), client_secret.strip())
    )

    if resp.status_code != 200:
        raise AppException(
            message=f"Token request failed for {login_endpoint} ({resp.status_code})",
            code="TOKEN_ERROR",
            status_code=502,
            retryable=False,
            context={"response": resp.text[:500]}
        )

    body = resp.json()
    return body["access_token"], int(body.get("expires_in", 300))



def exchange_code_for_token(code: str):
    token_url = f"https://{os.getenv('GENESYS_LOGIN_ENDPOINT')}/oauth/token"

    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": os.getenv("GENESYS_REDIRECT_URI"),
        "client_id": os.getenv("GENESYS_CLIENT_ID"),
        "client_secret": os.getenv("GENESYS_CLIENT_SECRET"),
    }
    print("token url = {token_url}")
    response = requests.post(token_url, data=payload)

    if response.status_code != 200:
        raise Exception("Failed to get token from Genesys")

    return response.json()



# --------------------------------------------------
# Create Genesys API Client
# --------------------------------------------------
def create_genesys_client(access_token: str, api_host: str) -> ApiClient:
    if not access_token:
        raise HTTPException(status_code=401, detail="Missing access token")

    host = api_host
    if not host:
        raise HTTPException(
            status_code=500,
            detail="GENESYS_API_HOST environment variable is not set"
        )

    api_client = ApiClient()
    print(f"api_client={api_client}")
    api_client.access_token = access_token
    api_client.host = host

    return api_client


# --------------------------------------------------
# 4) Simple in-memory token cache (no locks)
# --------------------------------------------------
@dataclass
class TokenEntry:
    access_token: str
    expires_at: float


class TokenServiceSimple:
    def __init__(self, refresh_buffer_seconds: int = 60):
        self._cache: Dict[str, TokenEntry] = {}
        self._buffer = refresh_buffer_seconds

    def invalidate(self, org_name: str) -> None:
        self._cache.pop(org_name, None)

    def get_token(self, org, force_refresh: bool = False) -> str:
        """
        org must have:
          org.org_name
          org.api_base_url
          org.client_id
          org.client_secret
        """
        now = time.time()
        cached = self._cache.get(org.org_name)

        # return cached token if still valid (with buffer)
        if not force_refresh and cached and now < (cached.expires_at - self._buffer):
            return cached.access_token

        # refresh token
        token, expires_in = get_client_credentials_token(
            api_base_url=org.api_base_url,
            client_id=org.client_id,
            client_secret=org.client_secret
        )

        self._cache[org.org_name] = TokenEntry(
            access_token=token,
            expires_at=time.time() + expires_in
        )
        return token



    
