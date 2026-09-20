"""Login application use case.

Coordinates authentication flow between domain ports and token service,
strictly enforcing anti-timing attack protection and unified error handling.
"""

from __future__ import annotations

from src.users.application.exceptions import InvalidCredentialsException
from src.users.application.ports.token_service import ITokenService
from src.users.domain.ports import IPasswordHasher, IUserRepository

# Pre-calculated 12-round bcrypt hash to ensure constant time execution
# when user is not found in database (mitigating timing attacks).
_DUMMY_BCRYPT_HASH = "$2b$12$EUMXXqgwf/iFTgmqUrJfdesyDvD46i98UD0xqvqrzj8N1c0x9Xl7e"


class LoginUseCase:
    """Use case to authenticate a user and issue a JWT token."""

    def __init__(
        self,
        user_repo: IUserRepository,
        password_hasher: IPasswordHasher,
        token_service: ITokenService,
    ) -> None:
        self.user_repo = user_repo
        self.password_hasher = password_hasher
        self.token_service = token_service

    def execute(self, email: str, password: str) -> str:
        """Authenticate user credentials and return an access token.

        Args:
            email: Plain email address from request.
            password: Plain password from request.

        Returns:
            Encoded JWT access token string.

        Raises:
            InvalidCredentialsException: If credentials are invalid or user not found.
        """
        user = self.user_repo.find_by_email(email)

        if user is None:
            # Timing attack countermeasure: execute dummy check with identical cost
            self.password_hasher.verify(password, _DUMMY_BCRYPT_HASH)
            raise InvalidCredentialsException()

        if not self.password_hasher.verify(password, user.password_hash):
            raise InvalidCredentialsException()

        return self.token_service.create_access_token({"sub": str(user.id)})
