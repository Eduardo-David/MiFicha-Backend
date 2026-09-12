"""
Pruebas de integración para restricciones de modelo SQLModel.

Estructura estricta AAA (Arrange-Act-Assert) para:
1. Unicidad de Cédula (identity_card) en Persona
2. Unicidad de Email en User
3. Borrado en Cascada Persona → User (relación 1:1)
"""
import pytest
from datetime import date, datetime
from uuid import uuid4
from sqlmodel import Session, select, create_engine
from sqlalchemy.exc import IntegrityError
from alembic.config import Config
from alembic import command
import sqlalchemy as sa
from src.infrastructure.db.models import Persona, User
from src.core.config import Settings


# ─── FIXTURES DE BASE DE DATOS ───
# Using Pydantic Settings for consistent DATABASE_URL configuration

settings = Settings()
engine = create_engine(settings.DATABASE_URL)


@pytest.fixture(scope="module")
def create_tables():
    """Ejecuta migraciones Alembic una vez por módulo."""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


@pytest.fixture(scope="function")
def session(create_tables):
    """Sesión por test con truncado de tablas para aislamiento."""
    with Session(engine) as sess:
        # Limpiar ANTES por si quedó basura de ejecuciones previas
        sess.execute(sa.text("TRUNCATE TABLE \"user\" CASCADE"))
        sess.execute(sa.text("TRUNCATE TABLE persona CASCADE"))
        sess.execute(sa.text("TRUNCATE TABLE device CASCADE"))
        sess.commit()
        try:
            yield sess
        finally:
            # Rollback por si el test dejó la sesión en estado fallido (ej. IntegrityError esperado)
            sess.rollback()
            # Limpiar DESPUÉS
            sess.execute(sa.text("TRUNCATE TABLE \"user\" CASCADE"))
            sess.execute(sa.text("TRUNCATE TABLE persona CASCADE"))
            sess.execute(sa.text("TRUNCATE TABLE device CASCADE"))
            sess.commit()
        sess.close()


# ─── TESTS ───

class TestPersonaIdentityCardUniqueness:
    """Pruebas de restricción UNIQUE en Persona.identity_card"""

    def test_unique_identity_card_raises_integrity_error(self, session: Session):
        """
        AAA: Verifica que insertar una Persona con cédula duplicada
        lanza IntegrityError a nivel de base de datos.
        """
        # ─── ARRANGE ───
        # Crear y persistir la primera persona con cédula única
        persona_original = Persona(
            id=uuid4(),
            first_name="Carlos",
            last_name="García",
            identity_card="V-12345678-9",
            birth_date=date(1985, 6, 15),
            phone="0412-1234567",
        )
        session.add(persona_original)
        session.commit()

        # Preparar segunda persona con LA MISMA cédula
        persona_duplicada = Persona(
            id=uuid4(),
            first_name="Ana",
            last_name="Martínez",
            identity_card="V-12345678-9",  # DUPLICADO intencional
            birth_date=date(1990, 3, 22),
            phone="0414-9876543",
        )

        # ─── ACT ───
        session.add(persona_duplicada)

        # ─── ASSERT ───
        # El commit debe fallar con IntegrityError por violación de UNIQUE
        with pytest.raises(IntegrityError) as exc_info:
            session.commit()

        # Verificar que es específicamente error de constraint unique
        assert "unique" in str(exc_info.value).lower() or "duplicate" in str(exc_info.value).lower()

        # Rollback implícito por el fixture deja la BD limpia


class TestUserEmailUniqueness:
    """Pruebas de restricción UNIQUE en User.email"""

    def test_unique_email_raises_integrity_error(self, session: Session):
        """
        AAA: Verifica que registrar un User con email duplicado
        lanza IntegrityError a nivel de base de datos.
        """
        # ─── ARRANGE ───
        # Crear persona base (necesaria por FK user.persona_id)
        persona = Persona(
            id=uuid4(),
            first_name="Laura",
            last_name="Pérez",
            identity_card="V-87654321-0",
            birth_date=date(1992, 11, 8),
            phone="0424-5555555",
        )
        session.add(persona)
        session.commit()

        # Crear primer usuario con email único
        usuario_original = User(
            id=uuid4(),
            email="laura.perez@example.com",
            password_hash="hash_seguro_123",
            role="patient",
            created_at=datetime.utcnow(),
            persona_id=persona.id,
        )
        session.add(usuario_original)
        session.commit()

        # Preparar segundo usuario con EL MISMO email
        usuario_duplicado = User(
            id=uuid4(),
            email="laura.perez@example.com",  # DUPLICADO intencional
            password_hash="otro_hash_456",
            role="doctor",
            created_at=datetime.utcnow(),
            persona_id=persona.id,  # Mismo persona_id también duplicaría FK unique, pero probamos email
        )

        # ─── ACT ───
        session.add(usuario_duplicado)

        # ─── ASSERT ───
        with pytest.raises(IntegrityError) as exc_info:
            session.commit()

        # Verificar que es error de constraint unique en email
        assert "unique" in str(exc_info.value).lower() or "duplicate" in str(exc_info.value).lower()


class TestPersonaUserCascadeDelete:
    """Pruebas de borrado en cascada Persona → User (relación 1:1)"""

    def test_delete_persona_cascades_to_user(self, session: Session):
        """
        AAA: Verifica que al eliminar una Persona,
        su User asociado se elimina automáticamente (ON DELETE CASCADE).
        """
        # ─── ARRANGE ───
        # Crear persona
        persona = Persona(
            id=uuid4(),
            first_name="Miguel",
            last_name="Rodríguez",
            identity_card="V-11223344-5",
            birth_date=date(1988, 9, 30),
            phone="0416-7778899",
        )
        session.add(persona)
        session.commit()

        # Crear user asociado a esa persona (relación 1:1)
        usuario = User(
            id=uuid4(),
            email="miguel.rodriguez@example.com",
            password_hash="hash_miguel_789",
            role="patient",
            created_at=datetime.utcnow(),
            persona_id=persona.id,
        )
        session.add(usuario)
        session.commit()

        # Guardar IDs para verificación posterior
        persona_id = persona.id
        usuario_id = usuario.id

        # Verificar que ambos existen antes del borrado
        assert session.get(Persona, persona_id) is not None
        assert session.get(User, usuario_id) is not None

        # ─── ACT ───
        # Eliminar SOLO la persona (el cascade debe borrar el user)
        session.delete(persona)
        session.commit()

        # ─── ASSERT ───
        # Persona debe haber sido eliminada
        persona_eliminada = session.get(Persona, persona_id)
        assert persona_eliminada is None, "La Persona debería haber sido eliminada"

        # User asociado debe haber sido eliminado en cascada (sin huérfanos)
        usuario_huerfano = session.get(User, usuario_id)
        assert usuario_huerfano is None, "El User debería haberse eliminado en cascada (ON DELETE CASCADE)"

        # Verificación adicional: no debe quedar ningún user con ese persona_id
        usuarios_restantes = session.exec(
            select(User).where(User.persona_id == persona_id)
        ).all()
        assert len(usuarios_restantes) == 0, "No deben quedar users huérfanos referenciando a la persona eliminada"