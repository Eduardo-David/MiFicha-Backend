"""JWT Token service adapter implemented with PyJWT."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt

from src.core.config import settings
from src.users.application.exceptions import InvalidTokenException
from src.users.application.ports.token_service import ITokenService


class PyJWTTokenService(ITokenService):
    """Token service adapter implementing ITokenService using PyJWT."""

    def __init__(
        self,
        secret_key: Optional[str] = None,
        algorithm: Optional[str] = None,
        expire_minutes: Optional[int] = None,
    ) -> None:
        self.secret_key = secret_key or settings.JWT_SECRET_KEY
        self.algorithm = algorithm or settings.JWT_ALGORITHM
        self.expire_minutes = expire_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create and sign a JWT access token.

        Args:
            data: Payload dictionary containing claims (e.g., {"sub": "<user_id>"}).

        Returns:
            Signed JWT string.
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token string.

        Args:
            token: Signed JWT string.

        Returns:
            Decoded payload claims.

        Raises:
            InvalidTokenException: If the token is invalid, corrupted, or expired.
        """
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.PyJWTError as exc:
            raise InvalidTokenException(str(exc)) from exc
