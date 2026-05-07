"""Tedo SDK error classes."""

from __future__ import annotations

from typing import Any


class TedoError(Exception):
    """Base error for all Tedo API errors."""

    code: str
    status_code: int
    details: dict[str, Any] | None
    request_id: str | None

    def __init__(
        self,
        message: str,
        *,
        code: str = "unknown_error",
        status_code: int = 0,
        details: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        self.request_id = request_id


class ValidationError(TedoError):
    """400 Bad Request."""


class AuthenticationError(TedoError):
    """401 Unauthorized."""


class PermissionError(TedoError):
    """403 Forbidden."""


class NotFoundError(TedoError):
    """404 Not Found."""


class RateLimitError(TedoError):
    """429 Too Many Requests."""


def parse_error(status_code: int, body: object) -> TedoError:
    """Parse an API error response into an idiomatic exception."""

    code = "unknown_error"
    message = f"API error {status_code}"
    details: dict[str, Any] | None = None
    request_id: str | None = None

    if isinstance(body, dict):
        raw_code = body.get("code", body.get("error"))
        if isinstance(raw_code, str) and raw_code:
            code = raw_code
        raw_message = body.get("message", body.get("error"))
        if isinstance(raw_message, str) and raw_message:
            message = raw_message
        raw_details = body.get("details")
        if isinstance(raw_details, dict):
            details = dict(raw_details)
        raw_request_id = body.get("request_id")
        if isinstance(raw_request_id, str):
            request_id = raw_request_id
    elif isinstance(body, str) and body:
        message = body

    error_cls: type[TedoError]
    if status_code == 400:
        error_cls = ValidationError
    elif status_code == 401:
        error_cls = AuthenticationError
    elif status_code == 403:
        error_cls = PermissionError
    elif status_code == 404:
        error_cls = NotFoundError
    elif status_code == 429:
        error_cls = RateLimitError
    else:
        error_cls = TedoError

    return error_cls(
        message,
        code=code,
        status_code=status_code,
        details=details,
        request_id=request_id,
    )
