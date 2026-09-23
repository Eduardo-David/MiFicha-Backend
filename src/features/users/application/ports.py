"""Port (abstract interface) for Token generation and validation.

Application use cases depend on this interface, decoupling the core logic
from any concrete JWT provider or cryptographic implementation.
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
