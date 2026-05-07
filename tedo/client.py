"""Core Tedo API client."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import time
from typing import Any

import httpx

from .billing import BillingService
from .errors import parse_error
from .projects import ProjectsService

DEFAULT_BASE_URL = "https://api.tedo.ai"


@dataclass(frozen=True)
class RetryConfig:
    """Retry policy for transient API responses."""

    max_retries: int = 3
    initial_backoff: float = 0.2
    max_backoff: float = 2.0


class Tedo:
    """Tedo API client."""

    billing: BillingService
    projects: ProjectsService

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        http_client: httpx.Client | None = None,
        retry: RetryConfig | None = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._http = http_client or httpx.Client()
        self._owns_http = http_client is None
        self._retry = retry or RetryConfig()

        self.billing = BillingService(self)
        self.projects = ProjectsService(self)

    def close(self) -> None:
        if self._owns_http:
            self._http.close()

    def __enter__(self) -> Tedo:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def _request(
        self,
        method: str,
        path: str,
        *,
        body: Mapping[str, Any] | None = None,
        query: Mapping[str, str] | None = None,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> dict[str, Any]:
        response = self._send(
            method,
            path,
            body=body,
            query=query,
            idempotency_key=idempotency_key,
            request_id=request_id,
            headers=headers,
        )
        if response.status_code == 204 or not response.content:
            return {}
        data = response.json()
        if isinstance(data, dict):
            return data
        return {"data": data}

    def _request_void(
        self,
        method: str,
        path: str,
        *,
        body: Mapping[str, Any] | None = None,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        self._send(
            method,
            path,
            body=body,
            idempotency_key=idempotency_key,
            request_id=request_id,
            headers=headers,
        )

    def _send(
        self,
        method: str,
        path: str,
        *,
        body: Mapping[str, Any] | None = None,
        query: Mapping[str, str] | None = None,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> httpx.Response:
        url = f"{self._base_url}{path}"
        request_headers = self._headers(
            idempotency_key=idempotency_key,
            request_id=request_id,
            headers=headers,
        )

        attempt = 0
        while True:
            response = self._http.request(
                method,
                url,
                json=dict(body) if body is not None else None,
                params=dict(query) if query is not None else None,
                headers=request_headers,
            )
            if response.status_code < 400:
                return response
            if not self._should_retry(response, attempt):
                raise parse_error(response.status_code, _response_body(response))
            time.sleep(self._retry_delay(response, attempt))
            attempt += 1

    def _headers(
        self,
        *,
        idempotency_key: str | None,
        request_id: str | None,
        headers: Mapping[str, str] | None,
    ) -> dict[str, str]:
        out = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if headers:
            out.update(headers)
        if idempotency_key:
            out["Idempotency-Key"] = idempotency_key
        if request_id:
            out["X-Request-ID"] = request_id
        return out

    def _should_retry(self, response: httpx.Response, attempt: int) -> bool:
        if attempt >= self._retry.max_retries:
            return False
        return response.status_code == 429 or 500 <= response.status_code < 600

    def _retry_delay(self, response: httpx.Response, attempt: int) -> float:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return max(0.0, float(retry_after))
            except ValueError:
                pass
        delay: float = self._retry.initial_backoff * (2**attempt)
        max_backoff: float = self._retry.max_backoff
        return delay if delay < max_backoff else max_backoff


def _response_body(response: httpx.Response) -> object:
    try:
        return response.json()
    except ValueError:
        return response.text
