from sqlalchemy.orm import Session
from application.ports import IDispositivoRepository

class PostgresDispositivoRepository(IDispositivoRepository):
    """Implementación del repositorio de Dispositivos usando PostgreSQL"""
    def __init__(self, session: Session):
        self._session = session

    def existeDispositivo(self, androidID: str) -> bool:
        # Aquí iría la lógica para comprobar si existe un dispositivo con el androidID dado
        query = self._session.query(Dispositivo).filter_by(android_id=androidID)
        return self._session.query(query.exists()).scalar()