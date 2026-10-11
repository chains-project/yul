"""Exceptions raised by the API client."""


class APIError(Exception):
    """Raised when the API returns an unexpected response."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
