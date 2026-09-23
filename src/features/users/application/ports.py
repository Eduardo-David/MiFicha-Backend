"""Ports (abstract interfaces) for Application layer services.

Application use cases depend on these interfaces, decoupling the core logic
from any concrete implementation (e.g. JWT, OCR, Transactions).
"""

from __future__ import annotations

import abc
from typing import Any, Dict


class ITokenService(abc.ABC):
    """Abstract interface for token operations."""

    @abc.abstractmethod
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create an encoded access token containing the provided payload data.

        Args:
            data: Payload claims to encode in the token.

        Returns:
            Encoded token string.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify the signature and validity of a token and return its claims.

        Args:
            token: Encoded token string.

        Returns:
            Decoded payload claims as a dictionary.

        Raises:
            Exception: If token is expired, invalid, or corrupted.
        """
        raise NotImplementedError


class IOCRService(abc.ABC):
    """Abstract interface for Optical Character Recognition services."""

    @abc.abstractmethod
    def verify_identity(self, identity_card: str, first_name: str, last_name: str) -> bool:
        """Verify the document data against the provided inputs.

        Args:
            identity_card: Document number.
            first_name: Person's first name.
            last_name: Person's last name.

        Returns:
            True if verification is successful.
        """
        raise NotImplementedError


class IUnitOfWork(abc.ABC):
    """Abstract interface for managing atomic database transactions."""

    @abc.abstractmethod
    def __enter__(self) -> IUnitOfWork:
        raise NotImplementedError

    @abc.abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def commit(self) -> None:
        """Commit the transaction."""
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self) -> None:
        """Rollback the transaction."""
        raise NotImplementedError
