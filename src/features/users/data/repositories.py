"""SQLModel/SQLAlchemy implementation of repositories and Unit of Work."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlmodel import Session, select

from src.features.users.data.models import (
    User as DbUser,
    Persona as DbPersona,
    Device as DbDevice,
)
from src.features.users.domain.models import (
    User as DomainUser,
    Persona as DomainPersona,
    Device as DomainDevice,
)
from src.features.users.domain.ports import (
    IUserRepository,
    IPersonaRepository,
    IDeviceRepository,
)
from src.features.users.application.ports import IUnitOfWork


class SqlAlchemyUnitOfWork(IUnitOfWork):
    """Manages database transactions."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def __enter__(self) -> IUnitOfWork:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self.rollback()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()


class SqlAlchemyUserRepository(IUserRepository):
    """Repository adapter backed by SQLModel/PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, user: DomainUser) -> None:
        """Persist or update a user."""
        statement = select(DbUser).where(DbUser.id == user.id)
        db_user = self.session.exec(statement).first()
        if db_user is None:
            db_user = DbUser(
                id=user.id,
                persona_id=user.persona_id,
                email=user.email,
                password_hash=user.password_hash,
                role=user.role,
            )
            self.session.add(db_user)
        else:
            db_user.email = user.email
            db_user.password_hash = user.password_hash
            db_user.role = user.role
        self.session.flush()

    def find_by_id(self, user_id: uuid.UUID) -> Optional[DomainUser]:
        """Find a user by id."""
        statement = select(DbUser).where(DbUser.id == user_id)
        db_user = self.session.exec(statement).first()
        if db_user is None:
            return None
        return DomainUser(
            id=db_user.id,
            persona_id=db_user.persona_id,
            email=db_user.email,
            password_hash=db_user.password_hash,
            role=db_user.role,
        )

    def find_by_email(self, email: str) -> Optional[DomainUser]:
        """Find a user by email address."""
        statement = select(DbUser).where(DbUser.email == email)
        db_user = self.session.exec(statement).first()
        if db_user is None:
            return None
        return DomainUser(
            id=db_user.id,
            persona_id=db_user.persona_id,
            email=db_user.email,
            password_hash=db_user.password_hash,
            role=db_user.role,
        )

    def delete(self, user_id: uuid.UUID) -> None:
        """Delete a user by id."""
        statement = select(DbUser).where(DbUser.id == user_id)
        db_user = self.session.exec(statement).first()
        if db_user:
            self.session.delete(db_user)
            self.session.flush()


class SqlAlchemyPersonaRepository(IPersonaRepository):
    """Persona repository adapter backed by SQLModel/PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, persona: DomainPersona) -> None:
        statement = select(DbPersona).where(DbPersona.id == persona.id)
        db_persona = self.session.exec(statement).first()
        if db_persona is None:
            db_persona = DbPersona(
                id=persona.id,
                first_name=persona.first_name,
                last_name=persona.last_name,
                identity_card=persona.identity_card,
                birth_date=persona.birth_date,
                phone=persona.phone,
            )
            self.session.add(db_persona)
        else:
            db_persona.first_name = persona.first_name
            db_persona.last_name = persona.last_name
            db_persona.identity_card = persona.identity_card
            db_persona.birth_date = persona.birth_date
            db_persona.phone = persona.phone
        self.session.flush()

    def find_by_id(self, persona_id: uuid.UUID) -> Optional[DomainPersona]:
        statement = select(DbPersona).where(DbPersona.id == persona_id)
        db_persona = self.session.exec(statement).first()
        if db_persona is None:
            return None
        domain = DomainPersona(
            id=db_persona.id,
            first_name=db_persona.first_name,
            last_name=db_persona.last_name,
            identity_card=db_persona.identity_card,
            email="", 
            phone=db_persona.phone or "",
        )
        domain.birth_date = db_persona.birth_date
        return domain

    def find_by_identity_card(self, identity_card: str) -> Optional[DomainPersona]:
        statement = select(DbPersona).where(DbPersona.identity_card == identity_card)
        db_persona = self.session.exec(statement).first()
        if db_persona is None:
            return None
        domain = DomainPersona(
            id=db_persona.id,
            first_name=db_persona.first_name,
            last_name=db_persona.last_name,
            identity_card=db_persona.identity_card,
            email="",
            phone=db_persona.phone or "",
        )
        domain.birth_date = db_persona.birth_date
        return domain


class SqlAlchemyDeviceRepository(IDeviceRepository):
    """Device repository adapter backed by SQLModel/PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, device: DomainDevice) -> None:
        statement = select(DbDevice).where(DbDevice.id == device.id)
        db_device = self.session.exec(statement).first()
        if db_device is None:
            db_device = DbDevice(
                id=device.id,
                user_id=device.user_id,
                android_id=device.android_id,
            )
            self.session.add(db_device)
        else:
            db_device.android_id = device.android_id
            db_device.user_id = device.user_id
        self.session.flush()

    def find_by_android_id(self, android_id: str) -> Optional[DomainDevice]:
        statement = select(DbDevice).where(DbDevice.android_id == android_id)
        db_device = self.session.exec(statement).first()
        if db_device is None:
            return None
        return DomainDevice(
            id=db_device.id,
            user_id=db_device.user_id,
            android_id=db_device.android_id,
        )

    def delete_by_user_id(self, user_id: uuid.UUID) -> None:
        statement = select(DbDevice).where(DbDevice.user_id == user_id)
        devices = self.session.exec(statement).all()
        for device in devices:
            self.session.delete(device)
        self.session.flush()
