"""Ports (abstract interfaces) for the User Management bounded context.

Infrastructure adapters must implement these interfaces.
Zero external dependencies: only Python standard library.
"""

from __future__ import annotations

import abc
import uuid
from typing import Optional

from .models import Device, User


class IPasswordHasher(abc.ABC):
    """Port for password hashing and verification."""

    @abc.abstractmethod
    def hash(self, password: str) -> str:
        """Hash a plain-text password.

        Args:
            password: Plain-text password.

        Returns:
            Hashed password string.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def verify(self, password: str, hashed: str) -> bool:
        """Verify a plain-text password against a hash.

        Args:
            password: Plain-text password to verify.
            hashed: Stored password hash.

        Returns:
            True if password matches hash, False otherwise.
        """
        raise NotImplementedError


class IUserRepository(abc.ABC):
    """Port for User persistence operations."""

    @abc.abstractmethod
    def save(self, user: User) -> None:
        """Persist a User entity.

        Args:
            user: User entity to save.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def find_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Find a User by its ID.

        Args:
            user_id: UUID of the user to find.

        Returns:
            User entity if found, None otherwise.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        """Find a User by email address.

        Args:
            email: Email address to search for.

        Returns:
            User entity if found, None otherwise.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, user_id: uuid.UUID) -> None:
        """Delete a User by its ID.

        Args:
            user_id: UUID of the user to delete.
        """
        raise NotImplementedError


class IDeviceRepository(abc.ABC):
    """Port for Device persistence operations."""

    @abc.abstractmethod
    def save(self, device: Device) -> None:
        """Persist a Device entity.

        Args:
            device: Device entity to save.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def find_by_android_id(self, android_id: str) -> Optional[Device]:
        """Find a Device by its Android hardware ID.

        Args:
            android_id: Unique Android device identifier.

        Returns:
            Device entity if found, None otherwise.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_by_user_id(self, user_id: uuid.UUID) -> None:
        """Delete all devices associated with a user.

        Args:
            user_id: UUID of the user whose devices to delete.
        """
        raise NotImplementedError