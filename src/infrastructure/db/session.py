"""Database session and engine management."""

from typing import Generator
from sqlmodel import Session, create_engine
from src.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=False)


def get_session() -> Generator[Session, None, None]:
    """Yield a database session."""
    with Session(engine) as session:
        yield session
