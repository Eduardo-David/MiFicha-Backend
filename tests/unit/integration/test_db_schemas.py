import pytest
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from src.infrastructure.db.models import Persona, User, Device
from src.core.config import Settings
from sqlalchemy import create_engine, text as sa_text
from alembic.config import Config
from alembic import command
import uuid
from datetime import date, datetime


@pytest.fixture(scope="module")
def engine():
    settings = Settings()
    engine = create_engine(settings.DATABASE_URL)
    yield engine
    engine.dispose()


@pytest.fixture(scope="module")
def create_tables(engine):
    # Run alembic migrations
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


@pytest.fixture(scope="function")
def session(engine, create_tables):
    """Sesión por test con truncado de tablas para aislamiento."""
    with Session(engine) as sess:
        # Limpiar ANTES por si quedó basura de ejecuciones previas
        sess.execute(sa_text("TRUNCATE TABLE \"user\" CASCADE"))
        sess.execute(sa_text("TRUNCATE TABLE persona CASCADE"))
        sess.execute(sa_text("TRUNCATE TABLE device CASCADE"))
        sess.commit()
        try:
            yield sess
        finally:
            # Rollback por si el test dejó la sesión en estado fallido
            sess.rollback()
            # Limpiar DESPUÉS
            sess.execute(sa_text("TRUNCATE TABLE \"user\" CASCADE"))
            sess.execute(sa_text("TRUNCATE TABLE persona CASCADE"))
            sess.execute(sa_text("TRUNCATE TABLE device CASCADE"))
            sess.commit()
        sess.close()


def test_insert_duplicate_identity_card(session):
    persona1 = Persona(
        first_name="John",
        last_name="Doe",
        identity_card="1234567-1B",
        birth_date=date(1990, 1, 1),
        phone="123456789"
    )
    session.add(persona1)
    session.commit()

    persona_duplicate = Persona(
        first_name="Jane",
        last_name="Smith",
        identity_card="1234567-1B",  # duplicate
        birth_date=date(1995, 5, 5),
        phone="987654321"
    )
    session.add(persona_duplicate)
    with pytest.raises(IntegrityError):
        session.commit()


def test_insert_duplicate_email(session):
    persona = Persona(
        first_name="Alice",
        last_name="Wonderland",
        identity_card="9876543-2A",
        birth_date=date(1992, 2, 2),
        phone="555555555"
    )
    session.add(persona)
    session.commit()

    user1 = User(
        email="alice@example.com",
        password_hash="hashed_pwd",
        role="patient",
        created_at=datetime.utcnow(),
        persona_id=persona.id
    )
    session.add(user1)
    session.commit()

    user_duplicate = User(
        email="alice@example.com",  # duplicate
        password_hash="hashed_pwd2",
        role="patient",
        created_at=datetime.utcnow(),
        persona_id=persona.id
    )
    session.add(user_duplicate)
    with pytest.raises(IntegrityError):
        session.commit()


def test_device_cascade_delete(session):
    persona = Persona(
        first_name="Bob",
        last_name="Builder",
        identity_card="1111111-9Z",
        birth_date=date(1985, 3, 3),
        phone=None
    )
    session.add(persona)
    session.commit()

    user = User(
        email="bob@example.com",
        password_hash="hashed_pw",
        role="doctor",
        created_at=datetime.utcnow(),
        persona_id=persona.id
    )
    session.add(user)
    session.commit()

    device = Device(
        android_id="device_xyz_999",
        user_id=user.id,
        linked_at=datetime.utcnow()
    )
    session.add(device)
    session.commit()

    # Delete user
    session.delete(user)
    session.commit()

    # Device should be deleted too
    device_check = session.exec(select(Device).where(Device.android_id == "device_xyz_999")).first()
    assert device_check is None
