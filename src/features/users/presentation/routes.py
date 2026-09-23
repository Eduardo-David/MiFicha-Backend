"""FastAPI router for Authentication and User API."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlmodel import Session

from src.core.database import get_session
from src.features.users.application.exceptions import InvalidCredentialsException
from src.features.users.application.login_use_case import LoginUseCase
from src.features.users.application.ports import ITokenService
from src.features.users.domain.ports import IPasswordHasher, IUserRepository
from src.features.users.data.auth.bcrypt_hasher import BcryptPasswordHasher
from src.features.users.data.auth.jwt_service import PyJWTTokenService
from src.features.users.data.repositories import SqlAlchemyUserRepository

router = APIRouter()


class UserLoginRequest(BaseModel):
    """Schema for user login credentials."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class TokenResponse(BaseModel):
    """Schema for successful authentication response."""

    access_token: str
    token_type: str = "bearer"


def get_user_repository(session: Session = Depends(get_session)) -> IUserRepository:
    """Dependency provider for IUserRepository."""
    return SqlAlchemyUserRepository(session)


def get_password_hasher() -> IPasswordHasher:
    """Dependency provider for IPasswordHasher."""
    return BcryptPasswordHasher()


def get_token_service() -> ITokenService:
    """Dependency provider for ITokenService."""
    return PyJWTTokenService()


def get_login_use_case(
    user_repo: IUserRepository = Depends(get_user_repository),
    password_hasher: IPasswordHasher = Depends(get_password_hasher),
    token_service: ITokenService = Depends(get_token_service),
) -> LoginUseCase:
    """Dependency provider for LoginUseCase."""
    return LoginUseCase(
        user_repo=user_repo,
        password_hasher=password_hasher,
        token_service=token_service,
    )


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(
    request: UserLoginRequest,
    use_case: LoginUseCase = Depends(get_login_use_case),
) -> TokenResponse:
    """Authenticate user with email and password and issue a JWT token.

    Args:
        request: UserLoginRequest with validated email and password.
        use_case: Injected LoginUseCase.

    Returns:
        TokenResponse with access token and token type.

    Raises:
        HTTPException: 401 if credentials are invalid or user not found.
    """
    try:
        access_token = use_case.execute(email=request.email, password=request.password)
        return TokenResponse(access_token=access_token, token_type="bearer")
    except InvalidCredentialsException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
