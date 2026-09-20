"""SQLModel/SQLAlchemy implementation of IUserRepository."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlmodel import Session, select

from src.infrastructure.db.models import User as DbUser
from src.users.domain.models import User as DomainUser
from src.users.domain.ports import IUserRepository


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
        self.session.commit()
        self.session.refresh(db_user)

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
            self.session.commit()
