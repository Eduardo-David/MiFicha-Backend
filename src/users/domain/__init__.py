"""User Management Domain Package.

Pure domain layer with zero external dependencies.
Exports: Entities, Exceptions, and Ports (interfaces).
"""

from .exceptions import (
    DomainException,
    RestriccionTiempoException,
    ValidationError,
)
from .models import Device, Persona, User
from .ports import IDeviceRepository, IPasswordHasher, IUserRepository

__all__ = [
    # Exceptions
    "DomainException",
    "ValidationError",
    "RestriccionTiempoException",
    # Entities
    "Persona",
    "User",
    "Device",
    # Ports
    "IPasswordHasher",
    "IUserRepository",
    "IDeviceRepository",
]