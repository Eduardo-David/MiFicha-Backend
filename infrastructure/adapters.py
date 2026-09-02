import hashlib
from application.ports import ICuentaRepository, IDispositivoRepository, IPasswordHasher
from domain.entities import Cuenta

class InMemoryCuentaRepository(ICuentaRepository):
    """Adaptador de Salida Mock: Repositorio en memoria para Cuentas."""
    
    def __init__(self):
        self.cuentas = []

    def guardar(self, cuenta: Cuenta) -> None:
        self.cuentas.append(cuenta)

class InMemoryDispositivoRepository(IDispositivoRepository):
    """Adaptador de Salida Mock: Repositorio en memoria para Dispositivos."""
    
    def __init__(self):
        self.dispositivos = set()

    def existeDispositivo(self, androidID: str) -> bool:
        return androidID in self.dispositivos
        
    def agregar_dispositivo(self, androidID: str):
        # Método utilitario para simular persistencia conjunta durante la prueba
        self.dispositivos.add(androidID)

class SHA256PasswordHasher(IPasswordHasher):
    """Adaptador de Salida: Implementación de hash usando hashlib (SHA256)."""
    
    def hashear(self, passwordPlano: str) -> str:
        return hashlib.sha256(passwordPlano.encode()).hexdigest()
