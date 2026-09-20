"""Bcrypt adapter implementing domain IPasswordHasher port."""

from __future__ import annotations

import bcrypt

from src.users.domain.ports import IPasswordHasher


class BcryptPasswordHasher(IPasswordHasher):
    """Password hasher adapter backed by bcrypt."""

    def hash(self, password: str) -> str:
        """Hash a plain-text password using bcrypt.

        Args:
            password: Plain-text password to hash.

        Returns:
            Hashed password string.
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def verify(self, password: str, hashed: str) -> bool:
        """Verify a plain-text password against a stored bcrypt hash.

        Args:
            password: Plain-text password to verify.
            hashed: Stored bcrypt hash string.

        Returns:
            True if matching, False otherwise.
        """
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
        except (ValueError, TypeError):
            return False
