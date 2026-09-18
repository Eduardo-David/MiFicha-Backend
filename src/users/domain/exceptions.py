"""Domain exceptions for the User Management bounded context."""

from datetime import timedelta
from typing import Optional


class DomainException(Exception):
    """Base exception for all domain errors."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ValidationError(DomainException):
    """Raised when constructors or inputs fail domain constraints."""

    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message)
        self.field = field


class RestriccionTiempoException(DomainException):
    """Raised when a profile update is requested before the 24-hour cooldown expires."""

    def __init__(self, time_remaining: timedelta):
        hours = int(time_remaining.total_seconds() // 3600)
        minutes = int((time_remaining.total_seconds() % 3600) // 60)
        message = (
            f"Profile modification is locked. "
            f"Please wait {hours}h {minutes}m remaining."
        )
        super().__init__(message)
        self.time_remaining = time_remaining