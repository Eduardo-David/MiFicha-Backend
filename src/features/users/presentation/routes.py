"""FastAPI routers for Authentication and User API."""

from __future__ import annotations

import uuid
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlmodel import Session

from src.core.database import get_session
from src.features.users.application.exceptions import (
    InvalidCredentialsException,
    EntityAlreadyExistsException,
    OCRVerificationFailedException,
)
from src.features.users.domain.exceptions import ValidationError
from src.features.users.application.login_use_case import LoginUseCase
from src.features.users.application.register_user_use_case import RegisterUserUseCase
from src.features.users.application.ports import ITokenService, IOCRService, IUnitOfWork
from src.features.users.domain.ports import (
    IPasswordHasher,
    IUserRepository,
    IPersonaRepository,
    IDeviceRepository,
)
from src.features.users.data.auth.bcrypt_hasher import BcryptPasswordHasher
from src.features.users.data.auth.jwt_service import PyJWTTokenService
from src.features.users.data.mock_ocr_service import MockOCRService
from src.features.users.data.repositories import (
    SqlAlchemyUserRepository,
    SqlAlchemyPersonaRepository,
    SqlAlchemyDeviceRepository,
    SqlAlchemyUnitOfWork,
)

auth_router = APIRouter()
users_router = APIRouter()


class UserLoginRequest(BaseModel):
    """Schema for user login credentials."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class TokenResponse(BaseModel):
    """Schema for successful authentication response."""
    access_token: str
    token_type: str = "bearer"


class UserRegisterRequest(BaseModel):
    """Schema for user registration."""
    first_name: str
    last_name: str
    identity_card: str
    birth_date: date
    phone: str
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    android_id: str = Field(..., min_length=1)


class UserRegisterResponse(BaseModel):
    """Schema for successful registration response."""
    id: uuid.UUID
    email: str
    role: str


# Dependency Providers
def get_user_repository(session: Session = Depends(get_session)) -> IUserRepository:
    return SqlAlchemyUserRepository(session)


def get_persona_repository(session: Session = Depends(get_session)) -> IPersonaRepository:
    return SqlAlchemyPersonaRepository(session)


def get_device_repository(session: Session = Depends(get_session)) -> IDeviceRepository:
    return SqlAlchemyDeviceRepository(session)


def get_password_hasher() -> IPasswordHasher:
    return BcryptPasswordHasher()


def get_token_service() -> ITokenService:
    return PyJWTTokenService()


def get_ocr_service() -> IOCRService:
    return MockOCRService()


def get_unit_of_work(session: Session = Depends(get_session)) -> IUnitOfWork:
    return SqlAlchemyUnitOfWork(session)


def get_login_use_case(
    user_repo: IUserRepository = Depends(get_user_repository),
    password_hasher: IPasswordHasher = Depends(get_password_hasher),
    token_service: ITokenService = Depends(get_token_service),
) -> LoginUseCase:
    return LoginUseCase(
        user_repo=user_repo,
        password_hasher=password_hasher,
        token_service=token_service,
    )


def get_register_user_use_case(
    uow: IUnitOfWork = Depends(get_unit_of_work),
    persona_repo: IPersonaRepository = Depends(get_persona_repository),
    user_repo: IUserRepository = Depends(get_user_repository),
    device_repo: IDeviceRepository = Depends(get_device_repository),
    password_hasher: IPasswordHasher = Depends(get_password_hasher),
    ocr_service: IOCRService = Depends(get_ocr_service),
) -> RegisterUserUseCase:
    return RegisterUserUseCase(
        uow=uow,
        persona_repo=persona_repo,
        user_repo=user_repo,
        device_repo=device_repo,
        password_hasher=password_hasher,
        ocr_service=ocr_service,
    )


@auth_router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(
    request: UserLoginRequest,
    use_case: LoginUseCase = Depends(get_login_use_case),
) -> TokenResponse:
    """Authenticate user with email and password and issue a JWT token."""
    try:
        access_token = use_case.execute(email=request.email, password=request.password)
        return TokenResponse(access_token=access_token, token_type="bearer")
    except InvalidCredentialsException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )


@users_router.post("", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    request: UserRegisterRequest,
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case),
) -> UserRegisterResponse:
    """Register a new user with OCR validation and device binding."""
    try:
        result = use_case.execute(request.model_dump())
        return UserRegisterResponse(**result)
    except EntityAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{e.field} is already registered"
        )
    except (OCRVerificationFailedException, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
