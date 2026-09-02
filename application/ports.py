from abc import ABC, abstractmethod
from domain.entities import Cuenta

class ICuentaRepository(ABC):
    """Puerto de salida para la persistencia de Cuenta."""
    
    @abstractmethod
    def guardar(self, cuenta: Cuenta) -> None:
        pass

class IDispositivoRepository(ABC):
    """Puerto de salida para consultas sobre Dispositivos."""
    
    @abstractmethod
    def existeDispositivo(self, androidID: str) -> bool:
        pass

class IPasswordHasher(ABC):
    """Puerto para la abstracción del hasheo de contraseñas."""
    
    @abstractmethod
    def hashear(self, passwordPlano: str) -> str:
        pass
