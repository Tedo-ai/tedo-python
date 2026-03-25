"""Tedo Python SDK."""

import requests
from .errors import TedoError, parse_error
from .billing import BillingService


class Tedo:
    """Tedo API client.

    Usage:
        client = Tedo(api_key="tedo_live_...", base_url="https://api.tedo.ai")
        plans = client.billing.list_plans()
    """

    def __init__(self, api_key: str, base_url: str = "https://api.tedo.ai",
                 verify_ssl: bool = True):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._verify_ssl = verify_ssl
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        self._session.verify = verify_ssl

        self.billing = BillingService(self)

    def _request(self, method: str, path: str, body: dict = None) -> dict:
        """Send a request and return the parsed JSON body."""
        url = f"{self._base_url}{path}"
        resp = self._session.request(method, url, json=body)

        if resp.status_code >= 400:
            try:
                error_body = resp.json()
            except Exception:
                error_body = {"error": resp.text}
            raise parse_error(resp.status_code, error_body)

        if resp.status_code == 204 or not resp.content:
            return {}
        return resp.json()

    def _request_void(self, method: str, path: str, body: dict = None):
        """Send a request that returns no body."""
        url = f"{self._base_url}{path}"
        resp = self._session.request(method, url, json=body)

        if resp.status_code >= 400:
            try:
                error_body = resp.json()
            except Exception:
                error_body = {"error": resp.text}
            raise parse_error(resp.status_code, error_body)
