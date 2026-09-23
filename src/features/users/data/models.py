from typing import Optional, List
from datetime import date, datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
import sqlalchemy as sa

class Persona(SQLModel, table=True):
    __tablename__ = "persona"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    first_name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)
    identity_card: str = Field(nullable=False, unique=True, index=True)
    birth_date: date = Field(nullable=False)
    phone: Optional[str] = None
    
    # Sin from __future__ import annotations, las forward refs se evalúan
    user: Optional["User"] = Relationship(
        back_populates="persona",
        sa_relationship_kwargs={"uselist": False, "foreign_keys": "User.persona_id", "cascade": "delete"}
    )

class User(SQLModel, table=True):
    __tablename__ = "user"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(nullable=False, unique=True, index=True)
    password_hash: str = Field(nullable=False)
    role: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    persona_id: UUID = Field(
        sa_column=sa.Column(sa.Uuid(), sa.ForeignKey("persona.id", ondelete="CASCADE"), nullable=False, unique=True)
    )

    persona: Optional["Persona"] = Relationship(back_populates="user")
    devices: List["Device"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "foreign_keys": "Device.user_id"}
    )

class Device(SQLModel, table=True):
    __tablename__ = "device"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    android_id: str = Field(nullable=False, unique=True, index=True)
    user_id: UUID = Field(
        sa_column=sa.Column(sa.Uuid(), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    )
    linked_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    user: Optional["User"] = Relationship(back_populates="devices")