from sqlalchemy.orm import Session
from application.ports import ICuentaRepository
from domain.entities import Cuenta

class PostgresCuentaRepository(ICuentaRepository):
    """Implementación del repositorio de Cuentas usando PostgreSQL"""
    def __init__(self, session: Session):
        self._session = session

    def guardar(self, cuenta: Cuenta) -> None:
        # Aquí iría la lógica para guardar una cuenta usando SQLAlchemy
        self._session.add(cuenta)
        self._session.commit()