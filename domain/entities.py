from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

@dataclass
class Persona:
    """Clase abstracta para representar a una persona."""
    id: str
    nombres: str
    apellidoPaterno: str
    apellidoMaterno: str
    telefono: str
    numeroCarnet: str
    fechaNacimiento: date

@dataclass
class Solicitante(Persona):
    """Representa al solicitante que reserva fichas médicas."""
    pass

@dataclass
class DispositivoMovil:
    """Representa el dispositivo desde el cual se usa la cuenta."""
    id: str
    androidID: str

@dataclass
class Cuenta:
    """Entidad principal que maneja la autenticación y vinculaciones."""
    id: str
    correo: str
    contrasenaHash: str
    fechaCreacion: datetime = field(default_factory=datetime.now)
    dispositivo: Optional[DispositivoMovil] = None
    solicitante: Optional[Solicitante] = None

    def vincularDispositivo(self, disp: DispositivoMovil) -> None:
        """Asigna un dispositivo móvil a la cuenta."""
        self.dispositivo = disp

    def asignarSolicitante(self, sol: Solicitante) -> None:
        """Asigna el perfil de solicitante a la cuenta."""
        self.solicitante = sol
