"""Tedo SDK error classes."""


class TedoError(Exception):
    """Base error for all Tedo API errors."""

    def __init__(self, message: str, status_code: int = 0):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(TedoError):
    """Resource not found (404)."""

    def __init__(self, message: str = "Not found"):
        super().__init__(message, 404)


class ValidationError(TedoError):
    """Validation error (422)."""

    def __init__(self, message: str = "Validation error"):
        super().__init__(message, 422)


class AuthenticationError(TedoError):
    """Authentication failed (401)."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, 401)


class RateLimitError(TedoError):
    """Rate limit exceeded (429)."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, 429)


def parse_error(status_code: int, body: dict) -> TedoError:
    """Parse an API error response into the appropriate exception."""
    message = body.get("error", body.get("message", f"API error {status_code}"))

    if status_code == 404:
        return NotFoundError(message)
    elif status_code == 422:
        return ValidationError(message)
    elif status_code == 401:
        return AuthenticationError(message)
    elif status_code == 429:
        return RateLimitError(message)
    else:
        return TedoError(message, status_code)
